"""
╔══════════════════════════════════════════════════════════════╗
║           🔨 Advanced Ban Management System                  ║
║    Prefix commands, Modals, Auto-Unban, Logging, SQLite      ║
╚══════════════════════════════════════════════════════════════╝

Commands:
  !ban       — Opens the ban panel (embed + buttons → modal)
  !forceban  — Bans a user by ID even if they left the server
  !cleanup   — Deletes recent messages from a specific user

Features:
  • Interactive modal for ban details (opens from button click)
  • Confirmation step before executing ban
  • Temporary & permanent bans with auto-unban scheduler
  • SQLite-backed storage for ban records
  • Rich audit logging to a dedicated channel
"""

import discord
from discord.ext import commands, tasks

import re
import os
import aiosqlite
from datetime import datetime, timedelta, timezone


# =========================
# 🎨 THEME CONSTANTS
# =========================

EMBED_COLOR         = 0x7C3AED   # Vibrant purple
EMBED_COLOR_SUCCESS = 0x10B981   # Emerald green
EMBED_COLOR_WARN    = 0xF59E0B   # Amber
EMBED_COLOR_DANGER  = 0xEF4444   # Red
FOOTER_TEXT         = "Ban Management ✦"

# Database path — created at runtime
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bans.db")


# ============================================================
#  HELPERS
# ============================================================

def parse_duration(text: str):
    """
    Parse a human-readable duration string into total seconds.
    Supports: 30m, 1h, 12h, 1d, 7d, 30d, permanent/perm
    Returns None for permanent bans.
    """
    text = text.strip().lower()
    if text in ("permanent", "perm", "forever", "0"):
        return None  # permanent

    pattern = re.compile(r"(\d+)\s*([mhd])")
    matches = pattern.findall(text)
    if not matches:
        raise ValueError(f"Invalid duration format: `{text}`. Use e.g. `30m`, `12h`, `1d`, `7d`, or `permanent`.")

    total = 0
    multipliers = {"m": 60, "h": 3600, "d": 86400}
    for amount, unit in matches:
        total += int(amount) * multipliers[unit]

    if total <= 0:
        raise ValueError("Duration must be greater than zero.")
    return total


def parse_delete_option(text: str) -> int:
    """
    Map the user's delete-messages choice to Discord's delete_message_seconds.
    Valid inputs: 'none' / '0', '24h' / '1d', '7d'
    """
    text = text.strip().lower()
    mapping = {
        "none": 0, "0": 0,
        "24h": 86400, "1d": 86400, "1 day": 86400,
        "7d": 604800, "7 days": 604800, "7days": 604800,
    }
    if text in mapping:
        return mapping[text]
    raise ValueError(f"Invalid delete option: `{text}`. Use `none`, `24h`, or `7d`.")


def format_duration(seconds):
    """Format seconds back to human-readable string."""
    if seconds is None:
        return "⛔ Permanent"
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts) or "< 1m"


async def resolve_user_from_interaction(interaction, user_input: str):
    """
    Resolve a user from an ID or mention string (used inside modals/buttons).
    Returns (discord.User | None, error_message | None)
    """
    user_input = user_input.strip()
    mention_match = re.match(r"<@!?(\d+)>", user_input)
    if mention_match:
        user_input = mention_match.group(1)

    if user_input.isdigit():
        user_id = int(user_input)
        member = interaction.guild.get_member(user_id)
        if member:
            return member, None
        try:
            user = await interaction.client.fetch_user(user_id)
            return user, None
        except discord.NotFound:
            return None, f"No user found with ID `{user_id}`."
        except discord.HTTPException:
            return None, f"Failed to fetch user `{user_id}` from Discord API."

    return None, f"Invalid input: `{user_input}`. Provide a valid User ID or @mention."


async def resolve_user_from_ctx(ctx, user_input: str):
    """
    Resolve a user from an ID or mention string (used in prefix commands).
    Returns (discord.User | None, error_message | None)
    """
    user_input = user_input.strip()
    mention_match = re.match(r"<@!?(\d+)>", user_input)
    if mention_match:
        user_input = mention_match.group(1)

    if user_input.isdigit():
        user_id = int(user_input)
        member = ctx.guild.get_member(user_id)
        if member:
            return member, None
        try:
            user = await ctx.bot.fetch_user(user_id)
            return user, None
        except discord.NotFound:
            return None, f"No user found with ID `{user_id}`."
        except discord.HTTPException:
            return None, f"Failed to fetch user `{user_id}` from Discord API."

    return None, f"Invalid input: `{user_input}`. Provide a valid User ID or @mention."


# ============================================================
#  DATABASE
# ============================================================

async def init_db():
    """Create the bans database and table if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL DEFAULT 'No reason provided',
                duration_seconds INTEGER,
                delete_seconds INTEGER DEFAULT 0,
                banned_at TEXT NOT NULL,
                unban_at TEXT,
                unbanned INTEGER DEFAULT 0
            )
        """)
        await db.commit()


async def insert_ban(user_id, guild_id, moderator_id, reason, duration_seconds, delete_seconds, unban_at):
    """Insert a new ban record into the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO bans (user_id, guild_id, moderator_id, reason, duration_seconds, delete_seconds, banned_at, unban_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, guild_id, moderator_id, reason, duration_seconds, delete_seconds,
            datetime.now(timezone.utc).isoformat(),
            unban_at.isoformat() if unban_at else None
        ))
        await db.commit()


async def get_expired_bans():
    """Get all temporary bans that have passed their unban_at time."""
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM bans
            WHERE unbanned = 0
              AND unban_at IS NOT NULL
              AND unban_at <= ?
        """, (now,)) as cursor:
            return await cursor.fetchall()


async def mark_unbanned(ban_id: int):
    """Mark a ban record as unbanned."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE bans SET unbanned = 1 WHERE id = ?", (ban_id,))
        await db.commit()


# ============================================================
#  VIEWS & MODALS
# ============================================================

class BanPanelView(discord.ui.View):
    """
    The initial !ban panel with two buttons:
      • Ban User — opens the ban modal
      • Cancel   — dismisses the panel
    """

    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only the command author can interact with this panel."""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Only the command user can use these buttons.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Ban User", emoji="🔨", style=discord.ButtonStyle.danger, row=0)
    async def ban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Permission check
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(
                "❌ You don't have **Ban Members** permission.", ephemeral=True
            )
            return
        await interaction.response.send_modal(BanModal())

    @discord.ui.button(label="Cancel", emoji="✖️", style=discord.ButtonStyle.secondary, row=0)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except discord.HTTPException:
            pass
        await interaction.response.send_message("❌ Ban panel cancelled.", ephemeral=True, delete_after=5)
        self.stop()


class BanModal(discord.ui.Modal, title="🔨 Ban User"):
    """
    Modal form with 4 fields:
      1. Target ID (Short Text, 18-digit Discord ID)
      2. Reason (Paragraph Text)
      3. Clean Old Messages? (Short Text: Yes or No)
      4. Days to Delete (Short Text: number 1–7)
    """

    user_input = discord.ui.TextInput(
        label="Target ID",
        placeholder="e.g. 123456789012345678",
        required=True,
        max_length=20,
        min_length=17,
    )
    reason_input = discord.ui.TextInput(
        label="Reason",
        placeholder="e.g. Repeated rule violations",
        required=True,
        max_length=512,
        style=discord.TextStyle.paragraph,
    )
    clean_input = discord.ui.TextInput(
        label="Clean Old Messages? (Yes or No)",
        placeholder="Yes or No",
        required=True,
        max_length=3,
        default="No",
    )
    days_input = discord.ui.TextInput(
        label="Days to Delete (1–7, only if Clean = Yes)",
        placeholder="e.g. 7",
        required=False,
        max_length=1,
        default="1",
    )

    async def on_submit(self, interaction: discord.Interaction):
        """Process modal submission — show a confirmation embed before banning."""

        # ── 1. Resolve the target user ──
        target, error = await resolve_user_from_interaction(interaction, self.user_input.value)
        if error:
            await interaction.response.send_message(f"❌ {error}", ephemeral=True)
            return

        # ── 2. Parse clean messages option ──
        clean_val = self.clean_input.value.strip().lower()
        if clean_val not in ("yes", "no"):
            await interaction.response.send_message("❌ 'Clean Old Messages' must be **Yes** or **No**.", ephemeral=True)
            return

        clean_messages = clean_val == "yes"
        delete_days = 0
        delete_seconds = 0

        if clean_messages:
            days_val = self.days_input.value.strip() if self.days_input.value else "1"
            if not days_val.isdigit() or not (1 <= int(days_val) <= 7):
                await interaction.response.send_message("❌ 'Days to Delete' must be a number between **1** and **7**.", ephemeral=True)
                return
            delete_days = int(days_val)
            delete_seconds = delete_days * 86400  # Convert days to seconds

        # ── 3. Safety checks ──
        guild = interaction.guild

        if target.id == guild.owner_id:
            await interaction.response.send_message(
                "❌ You cannot ban the **server owner**.", ephemeral=True
            )
            return

        if target.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ You cannot ban **yourself**.", ephemeral=True
            )
            return

        member = guild.get_member(target.id)
        if member:
            if member.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You cannot ban a user with **Administrator** permission.", ephemeral=True
                )
                return
            if member.top_role >= interaction.user.top_role and interaction.user.id != guild.owner_id:
                await interaction.response.send_message(
                    "❌ You cannot ban a user with an **equal or higher role** than yours.", ephemeral=True
                )
                return

        # ── 4. Build confirmation embed ──
        reason = self.reason_input.value
        delete_display = f"Yes — {delete_days} day(s)" if clean_messages else "No"

        confirm_embed = discord.Embed(
            title="⚠️  Confirm Ban",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Are you sure you want to ban this user?\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_WARN,
            timestamp=datetime.now(timezone.utc),
        )
        confirm_embed.add_field(name="👤 Target", value=f"{target.mention} (`{target.id}`)", inline=True)
        confirm_embed.add_field(name="🛡️ Moderator", value=interaction.user.mention, inline=True)
        confirm_embed.add_field(name="📝 Reason", value=reason, inline=False)
        confirm_embed.add_field(name="🗑️ Clean Messages", value=delete_display, inline=True)
        confirm_embed.set_footer(text=FOOTER_TEXT)

        if hasattr(target, 'display_avatar') and target.display_avatar:
            confirm_embed.set_thumbnail(url=target.display_avatar.url)

        # ── 5. Send confirmation with buttons ──
        view = BanConfirmView(
            target=target,
            reason=reason,
            duration_seconds=None,  # Permanent ban from modal
            delete_seconds=delete_seconds,
            delete_days=delete_days,
            clean_messages=clean_messages,
            unban_at=None,
            moderator=interaction.user,
        )
        await interaction.response.send_message(embed=confirm_embed, view=view, ephemeral=True)


class BanConfirmView(discord.ui.View):
    """
    Confirmation view shown after filling the ban modal.
    Two buttons: Confirm Ban / Cancel
    """

    def __init__(self, target, reason, duration_seconds, delete_seconds, unban_at, moderator, delete_days=0, clean_messages=False):
        super().__init__(timeout=60)
        self.target = target
        self.reason = reason
        self.duration_seconds = duration_seconds
        self.delete_seconds = delete_seconds
        self.delete_days = delete_days
        self.clean_messages = clean_messages
        self.unban_at = unban_at
        self.moderator = moderator

    @discord.ui.button(label="Confirm Ban", emoji="✅", style=discord.ButtonStyle.danger, row=0)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        target = self.target

        # ── Execute the ban ──
        try:
            # Try to DM the user before banning
            try:
                dm_embed = discord.Embed(
                    title="🔨 You Have Been Banned",
                    description=(
                        f"You have been banned from **{guild.name}**.\n\n"
                        f"**Reason:** {self.reason}\n"
                        f"**Duration:** {format_duration(self.duration_seconds)}"
                    ),
                    color=EMBED_COLOR_DANGER,
                    timestamp=datetime.now(timezone.utc),
                )
                dm_embed.set_footer(text=FOOTER_TEXT)
                await target.send(embed=dm_embed)
            except (discord.Forbidden, discord.HTTPException, AttributeError):
                pass  # Can't DM the user — proceed anyway

            await guild.ban(
                target,
                reason=f"{self.reason} | By: {self.moderator} | Duration: {format_duration(self.duration_seconds)}",
                delete_message_seconds=self.delete_seconds,
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to ban this user. Check my role hierarchy and permissions.",
                ephemeral=True,
            )
            return
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Ban failed: {e}", ephemeral=True)
            return

        # ── Save to database ──
        await insert_ban(
            user_id=target.id,
            guild_id=guild.id,
            moderator_id=self.moderator.id,
            reason=self.reason,
            duration_seconds=self.duration_seconds,
            delete_seconds=self.delete_seconds,
            unban_at=self.unban_at,
        )

        # ── Success embed ──
        success_embed = discord.Embed(
            title="✅  User Banned Successfully",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"**{target}** has been banned.\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_SUCCESS,
            timestamp=datetime.now(timezone.utc),
        )
        success_embed.add_field(name="👤 User", value=f"{target.mention} (`{target.id}`)", inline=True)
        success_embed.add_field(name="⏱️ Duration", value=format_duration(self.duration_seconds), inline=True)
        success_embed.set_footer(text=FOOTER_TEXT)
        await interaction.followup.send(embed=success_embed, ephemeral=True)

        # Disable buttons
        for item in self.children:
            item.disabled = True

        # ── Send audit log ──
        cog = interaction.client.get_cog("BanManager")
        if cog:
            await cog.send_ban_log(
                guild=guild,
                target=target,
                moderator=self.moderator,
                reason=self.reason,
                duration_seconds=self.duration_seconds,
                delete_seconds=self.delete_seconds,
            )
            # ── Send ban report to #ban-reports ──
            await cog.send_ban_report(
                guild=guild,
                target=target,
                moderator=self.moderator,
                reason=self.reason,
                delete_days=self.delete_days,
                clean_messages=self.clean_messages,
            )

    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary, row=0)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="❌ Ban cancelled.", embed=None, view=None
        )


# ============================================================
#  COG
# ============================================================

class BanManager(commands.Cog):
    """Advanced Ban Management System with UI components and automation."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        """Called when the cog is loaded — initialise database and start tasks."""
        await init_db()
        self.auto_unban_task.start()
        print("🔨 Ban Manager cog loaded — auto-unban task started.")

    async def cog_unload(self):
        """Called when the cog is unloaded — stop tasks."""
        self.auto_unban_task.cancel()
        print("🔨 Ban Manager cog unloaded.")

    # ────────────────────────────────────────────────
    #  LOGGING
    # ────────────────────────────────────────────────

    async def send_ban_log(self, guild, target, moderator, reason, duration_seconds, delete_seconds):
        """Send a detailed ban log embed to the configured log channel with fail-safe handling."""
        from Bot import BAN_LOG_CHANNEL_ID

        if BAN_LOG_CHANNEL_ID == 0:
            return

        channel = self.bot.get_channel(BAN_LOG_CHANNEL_ID)
        if channel is None:
            print(f"⚠️ Ban log channel {BAN_LOG_CHANNEL_ID} not found.")
            return

        delete_display_map = {0: "None", 86400: "Last 24 hours", 604800: "Last 7 days"}
        now = datetime.now(timezone.utc)

        # Determine duration display
        if duration_seconds is None:
            duration_display = "⛔ Permanent"
        else:
            duration_display = format_duration(duration_seconds)

        log_embed = discord.Embed(
            title="🔨  Ban Log",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"A user has been banned from the server.\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_DANGER,
            timestamp=now,
        )
        log_embed.add_field(name="👤 Banned User", value=f"{target.mention} (`{target.id}`)", inline=True)
        log_embed.add_field(name="🛡️ Moderator", value=f"{moderator.mention} (`{moderator.id}`)", inline=True)
        log_embed.add_field(name="📝 Reason", value=reason, inline=False)
        log_embed.add_field(name="⏱️ Duration", value=duration_display, inline=True)
        log_embed.add_field(name="🗑️ Messages Deleted", value=delete_display_map.get(delete_seconds, f"{delete_seconds // 86400} day(s)" if delete_seconds else "None"), inline=True)
        log_embed.add_field(name="📅 Time & Date", value=f"<t:{int(now.timestamp())}:F>", inline=False)

        if duration_seconds is not None:
            unban_time = now + timedelta(seconds=duration_seconds)
            log_embed.add_field(name="🔓 Auto-Unban", value=f"<t:{int(unban_time.timestamp())}:F>", inline=False)
        else:
            log_embed.add_field(name="🔓 Auto-Unban", value="Never (Permanent)", inline=False)

        log_embed.set_footer(text=FOOTER_TEXT)
        if hasattr(target, 'display_avatar') and target.display_avatar:
            log_embed.set_thumbnail(url=target.display_avatar.url)

        # Fail-safe: try twice, log error on failure
        for attempt in range(2):
            try:
                await channel.send(embed=log_embed)
                return  # Success
            except discord.HTTPException as e:
                if attempt == 0:
                    print(f"⚠️ Ban log send failed (attempt 1), retrying: {e}")
                else:
                    print(f"❌ Ban log send failed after 2 attempts: {e}")

    async def send_ban_report(self, guild, target, moderator, reason, delete_days=0, clean_messages=False):
        """Send a detailed ban report embed to the #ban-reports channel."""
        from Bot import BAN_REPORT_CHANNEL_ID

        if BAN_REPORT_CHANNEL_ID == 0:
            return

        channel = self.bot.get_channel(BAN_REPORT_CHANNEL_ID)
        if channel is None:
            print(f"⚠️ Ban report channel {BAN_REPORT_CHANNEL_ID} not found.")
            return

        now = datetime.now(timezone.utc)

        report_embed = discord.Embed(
            title="📊  Ban Report",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"A new ban has been executed.\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=0x5865F2,  # Discord Blurple for reports
            timestamp=now,
        )
        report_embed.add_field(name="👤 Banned User ID", value=f"`{target.id}`", inline=True)
        report_embed.add_field(name="🛡️ Moderator", value=f"{moderator.display_name} (`{moderator.id}`)", inline=True)
        report_embed.add_field(name="📝 Reason", value=reason, inline=False)
        report_embed.add_field(
            name="🗑️ Messages Deleted",
            value=f"{delete_days} day(s)" if clean_messages else "None",
            inline=True,
        )
        report_embed.add_field(name="📅 Time & Date", value=f"<t:{int(now.timestamp())}:F>", inline=True)
        report_embed.set_footer(text="Ban Report ✦")

        if hasattr(target, 'display_avatar') and target.display_avatar:
            report_embed.set_thumbnail(url=target.display_avatar.url)

        # Fail-safe: try twice
        for attempt in range(2):
            try:
                await channel.send(embed=report_embed)
                return
            except discord.HTTPException as e:
                if attempt == 0:
                    print(f"⚠️ Ban report send failed (attempt 1), retrying: {e}")
                else:
                    print(f"❌ Ban report send failed after 2 attempts: {e}")

    async def send_unban_log(self, guild, user_id, reason="Auto-unban: temporary ban expired"):
        """Send an unban log embed to the configured log channel."""
        from Bot import BAN_LOG_CHANNEL_ID

        if BAN_LOG_CHANNEL_ID == 0:
            return

        channel = self.bot.get_channel(BAN_LOG_CHANNEL_ID)
        if channel is None:
            return

        try:
            user = await self.bot.fetch_user(user_id)
            user_display = f"{user} (`{user_id}`)"
        except Exception:
            user_display = f"Unknown (`{user_id}`)"

        log_embed = discord.Embed(
            title="🔓  Auto-Unban Log",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"A user has been automatically unbanned.\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_SUCCESS,
            timestamp=datetime.now(timezone.utc),
        )
        log_embed.add_field(name="👤 User", value=user_display, inline=True)
        log_embed.add_field(name="📝 Reason", value=reason, inline=False)
        log_embed.set_footer(text=FOOTER_TEXT)

        try:
            await channel.send(embed=log_embed)
        except discord.HTTPException:
            pass

    # ────────────────────────────────────────────────
    #  AUTO-UNBAN BACKGROUND TASK
    # ────────────────────────────────────────────────

    @tasks.loop(seconds=30)
    async def auto_unban_task(self):
        """Check for expired temp bans every 30 seconds and unban them."""
        try:
            expired = await get_expired_bans()
            for ban_record in expired:
                ban_id = ban_record["id"]
                user_id = ban_record["user_id"]
                guild_id = ban_record["guild_id"]

                guild = self.bot.get_guild(guild_id)
                if guild is None:
                    continue

                try:
                    user = await self.bot.fetch_user(user_id)
                    await guild.unban(user, reason="Auto-unban: temporary ban expired")
                    print(f"🔓 Auto-unbanned user {user_id} in guild {guild_id}")
                    await self.send_unban_log(guild, user_id)
                except discord.NotFound:
                    print(f"⚠️ User {user_id} not found in ban list (may have been unbanned manually)")
                except discord.Forbidden:
                    print(f"⚠️ Missing permissions to unban user {user_id}")
                except discord.HTTPException as e:
                    print(f"⚠️ Failed to unban user {user_id}: {e}")

                await mark_unbanned(ban_id)
        except Exception as e:
            print(f"⚠️ Auto-unban task error: {e}")

    @auto_unban_task.before_loop
    async def before_auto_unban(self):
        await self.bot.wait_until_ready()

    # ────────────────────────────────────────────────
    #  PREFIX COMMAND: !ban
    # ────────────────────────────────────────────────

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_command(self, ctx):
        """Open the interactive ban management panel with buttons."""

        panel_embed = discord.Embed(
            title="🔨  Ban Management Panel",
            description=(
                "━━━━━━━━━━━━━━━━━━\n"
                "Use the buttons below to manage bans.\n\n"
                "**🔨 Ban User** — Open ban form\n"
                "**✖️ Cancel** — Close this panel\n"
                "━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR,
            timestamp=datetime.now(timezone.utc),
        )
        panel_embed.set_footer(text=FOOTER_TEXT)
        panel_embed.add_field(
            name="ℹ️ How it works",
            value=(
                "1️⃣ Click **Ban User**\n"
                "2️⃣ Fill in the ban details\n"
                "3️⃣ Review and confirm the ban"
            ),
            inline=False,
        )

        view = BanPanelView(author_id=ctx.author.id)
        await ctx.reply(embed=panel_embed, view=view, mention_author=False)

    # ────────────────────────────────────────────────
    #  PREFIX COMMAND: !forceban
    # ────────────────────────────────────────────────

    @commands.command(name="forceban")
    @commands.has_permissions(ban_members=True)
    async def forceban_command(self, ctx, user_id: str = None, reason: str = "No reason provided",
                                duration: str = "permanent", delete_messages: str = "none"):
        """Force-ban a user by ID, even if they've left the server.
        
        Usage: !forceban <user_id> [reason] [duration] [delete_messages]
        Example: !forceban 123456789 "Spam bot" 7d none
        """

        if user_id is None:
            em = discord.Embed(
                title="❌  Missing User ID",
                description=(
                    "**Usage:** `!forceban <user_id> [reason] [duration] [delete_messages]`\n\n"
                    "**Example:** `!forceban 123456789 \"Spam bot\" 7d none`\n\n"
                    "**Duration:** `30m`, `12h`, `1d`, `7d`, `permanent`\n"
                    "**Delete Messages:** `none`, `24h`, `7d`"
                ),
                color=EMBED_COLOR_DANGER,
            )
            em.set_footer(text=FOOTER_TEXT)
            await ctx.reply(embed=em, mention_author=False, delete_after=15)
            return

        # ── Validate user ID ──
        uid_str = user_id.strip()
        mention_match = re.match(r"<@!?(\d+)>", uid_str)
        if mention_match:
            uid_str = mention_match.group(1)

        if not uid_str.isdigit():
            await ctx.reply(f"❌ Invalid User ID: `{uid_str}`. Must be a numeric ID.", delete_after=10, mention_author=False)
            return

        uid = int(uid_str)

        # ── Safety checks ──
        if uid == ctx.guild.owner_id:
            await ctx.reply("❌ You cannot ban the **server owner**.", delete_after=10, mention_author=False)
            return
        if uid == ctx.author.id:
            await ctx.reply("❌ You cannot ban **yourself**.", delete_after=10, mention_author=False)
            return

        # ── Parse duration ──
        try:
            duration_seconds = parse_duration(duration)
        except ValueError as e:
            await ctx.reply(f"❌ {e}", delete_after=10, mention_author=False)
            return

        # ── Parse delete option ──
        try:
            delete_secs = parse_delete_option(delete_messages)
        except ValueError as e:
            await ctx.reply(f"❌ {e}", delete_after=10, mention_author=False)
            return

        # ── Fetch user from Discord ──
        try:
            user = await self.bot.fetch_user(uid)
        except discord.NotFound:
            await ctx.reply(f"❌ No Discord user found with ID `{uid}`.", delete_after=10, mention_author=False)
            return
        except discord.HTTPException as e:
            await ctx.reply(f"❌ Failed to fetch user: {e}", delete_after=10, mention_author=False)
            return

        # ── Execute force-ban ──
        try:
            await ctx.guild.ban(
                user,
                reason=f"{reason} | Forced by: {ctx.author} | Duration: {format_duration(duration_seconds)}",
                delete_message_seconds=delete_secs,
            )
        except discord.Forbidden:
            await ctx.reply("❌ I don't have permission to ban this user. Check my role hierarchy.", delete_after=10, mention_author=False)
            return
        except discord.HTTPException as e:
            await ctx.reply(f"❌ Ban failed: {e}", delete_after=10, mention_author=False)
            return

        # ── Database ──
        unban_at = None
        if duration_seconds is not None:
            unban_at = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)

        await insert_ban(
            user_id=uid,
            guild_id=ctx.guild.id,
            moderator_id=ctx.author.id,
            reason=reason,
            duration_seconds=duration_seconds,
            delete_seconds=delete_secs,
            unban_at=unban_at,
        )

        # ── Success embed ──
        success_embed = discord.Embed(
            title="✅  Force-Ban Successful",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"**{user}** (`{uid}`) has been force-banned.\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_SUCCESS,
            timestamp=datetime.now(timezone.utc),
        )
        success_embed.add_field(name="📝 Reason", value=reason, inline=False)
        success_embed.add_field(name="⏱️ Duration", value=format_duration(duration_seconds), inline=True)
        success_embed.set_footer(text=FOOTER_TEXT)
        await ctx.reply(embed=success_embed, mention_author=False)

        # ── Log ──
        await self.send_ban_log(
            guild=ctx.guild,
            target=user,
            moderator=ctx.author,
            reason=f"[FORCE-BAN] {reason}",
            duration_seconds=duration_seconds,
            delete_seconds=delete_secs,
        )

    # ────────────────────────────────────────────────
    #  PREFIX COMMAND: !cleanup
    # ────────────────────────────────────────────────

    @commands.command(name="cleanup")
    @commands.has_permissions(manage_messages=True)
    async def cleanup_command(self, ctx, user_id: str = None, limit: int = 100):
        """Delete recent messages from a specific user in this channel.
        
        Usage: !cleanup <user_id> [limit]
        Example: !cleanup 123456789 50
        """

        if user_id is None:
            em = discord.Embed(
                title="❌  Missing User ID",
                description=(
                    "**Usage:** `!cleanup <user_id> [limit]`\n\n"
                    "**Example:** `!cleanup 123456789 50`\n\n"
                    "Scans up to `limit` messages (default 100, max 500) and\n"
                    "deletes all messages from the specified user."
                ),
                color=EMBED_COLOR_DANGER,
            )
            em.set_footer(text=FOOTER_TEXT)
            await ctx.reply(embed=em, mention_author=False, delete_after=15)
            return

        # ── Validate user ID ──
        uid_str = user_id.strip()
        mention_match = re.match(r"<@!?(\d+)>", uid_str)
        if mention_match:
            uid_str = mention_match.group(1)

        if not uid_str.isdigit():
            await ctx.reply(f"❌ Invalid User ID: `{uid_str}`.", delete_after=10, mention_author=False)
            return

        uid = int(uid_str)
        limit = max(1, min(limit, 500))  # Clamp 1–500

        # ── Purge messages ──
        def check(msg):
            return msg.author.id == uid

        try:
            deleted = await ctx.channel.purge(limit=limit, check=check)
        except discord.Forbidden:
            await ctx.reply("❌ I don't have permission to delete messages in this channel.", delete_after=10, mention_author=False)
            return
        except discord.HTTPException as e:
            await ctx.reply(f"❌ Cleanup failed: {e}", delete_after=10, mention_author=False)
            return

        cleanup_embed = discord.Embed(
            title="🧹  Cleanup Complete",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Deleted **{len(deleted)}** messages from user `{uid}`\n"
                f"in {ctx.channel.mention}.\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_SUCCESS,
            timestamp=datetime.now(timezone.utc),
        )
        cleanup_embed.add_field(name="🛡️ Moderator", value=ctx.author.mention, inline=True)
        cleanup_embed.add_field(name="🔍 Scanned", value=f"Up to {limit} messages", inline=True)
        cleanup_embed.set_footer(text=FOOTER_TEXT)
        temp = await ctx.send(embed=cleanup_embed)
        await temp.delete(delay=15)

    # ── Error handlers ──

    @ban_command.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ You need the **Ban Members** permission to use this command.", delete_after=8, mention_author=False)

    @forceban_command.error
    async def forceban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ You need the **Ban Members** permission to use this command.", delete_after=8, mention_author=False)

    @cleanup_command.error
    async def cleanup_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ You need the **Manage Messages** permission to use this command.", delete_after=8, mention_author=False)


# ============================================================
#  COG SETUP
# ============================================================

async def setup(bot: commands.Bot):
    """Standard discord.py cog setup function."""
    await bot.add_cog(BanManager(bot))
    print("✅ Ban Manager cog registered.")
