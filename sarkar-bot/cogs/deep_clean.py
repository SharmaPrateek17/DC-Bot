"""
╔══════════════════════════════════════════════════════════════╗
║           🧹 Deep Clean — Advanced Moderation Tool           ║
║   Panel → Modal → Confirm → Live Progress → Completion Log  ║
╚══════════════════════════════════════════════════════════════╝

Command:
  !deepclean  — Opens the deep clean panel

Flow:
  1. Embed panel with "Start Cleanup" button
  2. Modal: User ID, Scan Limit, Reason
  3. Confirmation embed with Confirm / Cancel
  4. Live-updating progress embed
  5. Completion summary + mod-log entry
"""

import discord
from discord.ext import commands

import re
import asyncio
import time
from datetime import datetime, timezone, timedelta


# =========================
# 🎨 THEME
# =========================

EMBED_COLOR         = 0x7C3AED   # Vibrant purple
EMBED_COLOR_SUCCESS = 0x10B981   # Emerald green
EMBED_COLOR_WARN    = 0xF59E0B   # Amber
EMBED_COLOR_DANGER  = 0xEF4444   # Red
EMBED_COLOR_PROGRESS = 0x3B82F6  # Blue
FOOTER_TEXT         = "Deep Clean ✦"


# ============================================================
#  VIEWS & MODALS
# ============================================================

class DeepCleanPanelView(discord.ui.View):
    """
    Initial panel shown by !deepclean.
    Single button: "Start Cleanup" → opens modal.
    """

    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Only the command user can interact with this panel.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Start Cleanup", emoji="🧹", style=discord.ButtonStyle.primary, row=0)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Permission guard
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ You need **Manage Messages** permission.", ephemeral=True
            )
            return
        await interaction.response.send_modal(DeepCleanModal())

    @discord.ui.button(label="Cancel", emoji="✖️", style=discord.ButtonStyle.secondary, row=0)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except discord.HTTPException:
            pass
        await interaction.response.send_message("❌ Deep clean cancelled.", ephemeral=True, delete_after=5)
        self.stop()


class DeepCleanModal(discord.ui.Modal, title="🧹 Deep Clean Setup"):
    """
    Modal form with 3 fields:
      1. User ID (required)
      2. Messages per channel to scan (optional, default 100)
      3. Reason (optional)
    """

    user_id_input = discord.ui.TextInput(
        label="User ID",
        placeholder="e.g. 123456789012345678",
        required=True,
        max_length=24,
    )
    limit_input = discord.ui.TextInput(
        label="Messages to scan per channel",
        placeholder="Default: 100 (max 1000)",
        required=False,
        max_length=5,
        default="100",
    )
    reason_input = discord.ui.TextInput(
        label="Reason (for logging)",
        placeholder="e.g. Spam cleanup",
        required=False,
        max_length=256,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # ── Parse User ID ──
        uid_str = self.user_id_input.value.strip()
        mention_match = re.match(r"<@!?(\d+)>", uid_str)
        if mention_match:
            uid_str = mention_match.group(1)

        if not uid_str.isdigit():
            await interaction.response.send_message(
                f"❌ Invalid User ID: `{uid_str}`. Must be a numeric ID.", ephemeral=True
            )
            return

        user_id = int(uid_str)

        # ── Parse limit ──
        limit_str = self.limit_input.value.strip() or "100"
        if not limit_str.isdigit():
            await interaction.response.send_message(
                f"❌ Invalid scan limit: `{limit_str}`. Must be a number.", ephemeral=True
            )
            return
        scan_limit = max(1, min(int(limit_str), 1000))

        # ── Reason ──
        reason = self.reason_input.value.strip() or "No reason provided"

        # ── Resolve user display name ──
        try:
            user = await interaction.client.fetch_user(user_id)
            user_display = f"{user} (`{user_id}`)"
        except Exception:
            user_display = f"Unknown User (`{user_id}`)"

        # ── Count text channels ──
        text_channels = [
            ch for ch in interaction.guild.text_channels
            if ch.permissions_for(interaction.guild.me).read_message_history
            and ch.permissions_for(interaction.guild.me).manage_messages
        ]

        # ── Confirmation embed ──
        confirm_embed = discord.Embed(
            title="⚠️  Confirm Deep Clean",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "This will scan **all text channels** and delete\n"
                "messages from the specified user.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_WARN,
            timestamp=datetime.now(timezone.utc),
        )
        confirm_embed.add_field(name="👤 Target User", value=user_display, inline=True)
        confirm_embed.add_field(name="🔍 Scan Limit", value=f"{scan_limit} msgs/channel", inline=True)
        confirm_embed.add_field(name="📂 Channels", value=f"{len(text_channels)} accessible", inline=True)
        confirm_embed.add_field(name="📝 Reason", value=reason, inline=False)
        confirm_embed.add_field(
            name="⚠️ Warning",
            value="This action **cannot be undone**. Messages older than 14 days will be deleted individually (slower).",
            inline=False,
        )
        confirm_embed.set_footer(text=FOOTER_TEXT)

        view = DeepCleanConfirmView(
            user_id=user_id,
            user_display=user_display,
            scan_limit=scan_limit,
            reason=reason,
            moderator=interaction.user,
            text_channels=text_channels,
        )
        await interaction.response.send_message(embed=confirm_embed, view=view, ephemeral=True)


class DeepCleanConfirmView(discord.ui.View):
    """Confirm / Cancel buttons before executing the deep clean."""

    def __init__(self, user_id, user_display, scan_limit, reason, moderator, text_channels):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.user_display = user_display
        self.scan_limit = scan_limit
        self.reason = reason
        self.moderator = moderator
        self.text_channels = text_channels

    @discord.ui.button(label="Confirm", emoji="✅", style=discord.ButtonStyle.danger, row=0)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable buttons immediately
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        # Start the deep clean in the channel (not ephemeral, so we can edit it live)
        cog = interaction.client.get_cog("DeepClean")
        if cog:
            await cog.execute_deep_clean(
                channel=interaction.channel,
                user_id=self.user_id,
                user_display=self.user_display,
                scan_limit=self.scan_limit,
                reason=self.reason,
                moderator=self.moderator,
                text_channels=self.text_channels,
                guild=interaction.guild,
            )

    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary, row=0)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="❌ Deep clean cancelled.", embed=None, view=None
        )


# ============================================================
#  COG
# ============================================================

class DeepClean(commands.Cog):
    """Advanced moderation tool — deep clean a user's messages across all channels."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ────────────────────────────────────────────────
    #  PREFIX COMMAND: !deepclean
    # ────────────────────────────────────────────────

    @commands.command(name="deepclean")
    @commands.has_permissions(manage_messages=True)
    async def deepclean_command(self, ctx):
        """Open the deep clean moderation panel."""

        panel_embed = discord.Embed(
            title="🧹  Deep Clean",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Remove a user's messages from **every channel**\n"
                "in the server — even if they've left or been banned.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR,
            timestamp=datetime.now(timezone.utc),
        )
        panel_embed.add_field(
            name="How it works",
            value=(
                "1. Click **Start Cleanup**\n"
                "2. Enter the user ID and scan settings\n"
                "3. Review and confirm\n"
                "4. Watch progress in real-time"
            ),
            inline=False,
        )
        panel_embed.set_footer(text=FOOTER_TEXT)

        view = DeepCleanPanelView(author_id=ctx.author.id)
        await ctx.reply(embed=panel_embed, view=view, mention_author=False)

    @deepclean_command.error
    async def deepclean_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "❌ You need the **Manage Messages** permission to use this command.",
                delete_after=8, mention_author=False,
            )

    # ────────────────────────────────────────────────
    #  EXECUTE DEEP CLEAN
    # ────────────────────────────────────────────────

    async def execute_deep_clean(self, channel, user_id, user_display, scan_limit,
                                  reason, moderator, text_channels, guild):
        """
        Core deep clean logic:
          1. Send a progress embed
          2. Loop all text channels
          3. Delete matching messages (bulk < 14 days, individual > 14 days)
          4. Update progress embed periodically
          5. Send completion summary + mod-log
        """

        start_time = time.monotonic()
        total_deleted = 0
        channels_scanned = 0
        total_channels = len(text_channels)
        errors = []

        # ── Progress embed ──
        progress_embed = discord.Embed(
            title="🔄  Deep Clean — In Progress",
            description=(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Target: {user_display}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_PROGRESS,
            timestamp=datetime.now(timezone.utc),
        )
        progress_embed.add_field(name="📂 Channels", value=f"0 / {total_channels}", inline=True)
        progress_embed.add_field(name="🗑️ Deleted", value="0", inline=True)
        progress_embed.add_field(name="📍 Status", value="Starting...", inline=True)
        progress_embed.set_footer(text=FOOTER_TEXT)

        progress_msg = await channel.send(embed=progress_embed)

        # ── 14-day cutoff for bulk delete ──
        bulk_cutoff = datetime.now(timezone.utc) - timedelta(days=14)

        for ch in text_channels:
            channels_scanned += 1
            channel_deleted = 0

            try:
                # Collect messages from this user
                recent_msgs = []   # < 14 days old → can bulk delete
                old_msgs = []      # > 14 days old → must delete individually

                async for msg in ch.history(limit=scan_limit):
                    if msg.author.id == user_id:
                        if msg.created_at.replace(tzinfo=timezone.utc) > bulk_cutoff:
                            recent_msgs.append(msg)
                        else:
                            old_msgs.append(msg)

                # ── Bulk delete recent messages (batches of 100) ──
                for i in range(0, len(recent_msgs), 100):
                    batch = recent_msgs[i:i+100]
                    if len(batch) == 1:
                        try:
                            await batch[0].delete()
                            channel_deleted += 1
                        except discord.HTTPException:
                            pass
                    elif len(batch) > 1:
                        try:
                            await ch.delete_messages(batch)
                            channel_deleted += len(batch)
                        except discord.HTTPException:
                            # Fallback: delete individually
                            for msg in batch:
                                try:
                                    await msg.delete()
                                    channel_deleted += 1
                                except discord.HTTPException:
                                    pass
                                await asyncio.sleep(0.3)

                # ── Delete old messages individually ──
                for msg in old_msgs:
                    try:
                        await msg.delete()
                        channel_deleted += 1
                    except discord.HTTPException:
                        pass
                    await asyncio.sleep(0.5)  # Rate limit safety

            except discord.Forbidden:
                errors.append(f"No access to #{ch.name}")
            except Exception as e:
                errors.append(f"#{ch.name}: {str(e)[:50]}")

            total_deleted += channel_deleted

            # ── Update progress every 3 channels or on last channel ──
            if channels_scanned % 3 == 0 or channels_scanned == total_channels:
                elapsed = time.monotonic() - start_time
                mins, secs = divmod(int(elapsed), 60)

                progress_embed.set_field_at(0, name="📂 Channels", value=f"{channels_scanned} / {total_channels}", inline=True)
                progress_embed.set_field_at(1, name="🗑️ Deleted", value=str(total_deleted), inline=True)

                if channels_scanned == total_channels:
                    progress_embed.set_field_at(2, name="📍 Status", value="Finishing...", inline=True)
                else:
                    progress_embed.set_field_at(2, name="📍 Status", value=f"Scanning #{ch.name}...", inline=True)

                try:
                    await progress_msg.edit(embed=progress_embed)
                except discord.HTTPException:
                    pass

        # ── Completion ──
        elapsed = time.monotonic() - start_time
        mins, secs = divmod(int(elapsed), 60)
        time_display = f"{mins}m {secs}s" if mins else f"{secs}s"

        # ── Update progress embed to completed ──
        done_embed = discord.Embed(
            title="✅  Deep Clean — Complete",
            description=(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"All channels have been processed.\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_SUCCESS,
            timestamp=datetime.now(timezone.utc),
        )
        done_embed.add_field(name="👤 Target", value=user_display, inline=True)
        done_embed.add_field(name="🛡️ Moderator", value=moderator.mention, inline=True)
        done_embed.add_field(name="🗑️ Messages Deleted", value=str(total_deleted), inline=True)
        done_embed.add_field(name="📂 Channels Scanned", value=str(channels_scanned), inline=True)
        done_embed.add_field(name="⏱️ Time", value=time_display, inline=True)
        done_embed.add_field(name="📝 Reason", value=reason, inline=True)

        if errors:
            error_text = "\n".join(errors[:5])
            if len(errors) > 5:
                error_text += f"\n... and {len(errors) - 5} more"
            done_embed.add_field(name="⚠️ Errors", value=f"```{error_text}```", inline=False)

        done_embed.set_footer(text=FOOTER_TEXT)

        try:
            await progress_msg.edit(embed=done_embed)
        except discord.HTTPException:
            await channel.send(embed=done_embed)

        # ── Send to mod-log channel ──
        await self.send_mod_log(
            guild=guild,
            user_display=user_display,
            user_id=user_id,
            moderator=moderator,
            total_deleted=total_deleted,
            channels_scanned=channels_scanned,
            time_display=time_display,
            reason=reason,
        )

    # ────────────────────────────────────────────────
    #  MOD LOG
    # ────────────────────────────────────────────────

    async def send_mod_log(self, guild, user_display, user_id, moderator,
                            total_deleted, channels_scanned, time_display, reason):
        """Send a deep clean summary to the mod-log channel."""
        from Bot import BAN_LOG_CHANNEL_ID

        if BAN_LOG_CHANNEL_ID == 0:
            return

        channel = self.bot.get_channel(BAN_LOG_CHANNEL_ID)
        if channel is None:
            return

        log_embed = discord.Embed(
            title="🧹  Deep Clean Log",
            description=(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"A deep clean operation was performed.\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_PROGRESS,
            timestamp=datetime.now(timezone.utc),
        )
        log_embed.add_field(name="👤 Target", value=user_display, inline=True)
        log_embed.add_field(name="🛡️ Moderator", value=f"{moderator} (`{moderator.id}`)", inline=True)
        log_embed.add_field(name="🗑️ Messages Deleted", value=str(total_deleted), inline=True)
        log_embed.add_field(name="📂 Channels Scanned", value=str(channels_scanned), inline=True)
        log_embed.add_field(name="⏱️ Duration", value=time_display, inline=True)
        log_embed.add_field(name="📝 Reason", value=reason, inline=True)
        log_embed.set_footer(text=FOOTER_TEXT)

        try:
            await channel.send(embed=log_embed)
        except discord.HTTPException as e:
            print(f"⚠️ Failed to send deep clean log: {e}")


# ============================================================
#  COG SETUP
# ============================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(DeepClean(bot))
    print("✅ Deep Clean cog registered.")
