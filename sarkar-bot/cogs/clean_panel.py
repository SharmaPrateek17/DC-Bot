"""
╔══════════════════════════════════════════════════════════════╗
║        🧹 Clean Panel — Interactive Message Management       ║
║   Panel → Modal flow for user, link, and channel cleaning    ║
╚══════════════════════════════════════════════════════════════╝

Command:
  !clean  (aliases: !purge, !clear)

Modes:
  1. Clean User Messages  — Delete msgs by User ID (works if they left)
  2. Delete by Link       — Paste a message link, deleted from server
  3. Purge Channel        — Bulk delete N messages in current channel
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
FOOTER_TEXT         = "Clean Panel ✦"

# Regex for Discord message links
# https://discord.com/channels/SERVER_ID/CHANNEL_ID/MESSAGE_ID
LINK_PATTERN = re.compile(
    r"https?://(?:ptb\.|canary\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)"
)


# ============================================================
#  PANEL VIEW (3 buttons + cancel)
# ============================================================

class CleanPanelView(discord.ui.View):
    """
    Main panel for !clean:
      • 👤 Clean User Messages — modal
      • 🔗 Delete by Link — modal
      • 📄 Purge Channel — modal
      • ✖️ Cancel
    """

    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Only the command user can interact.", ephemeral=True
            )
            return False
        return True

    # ── 1. Clean User Messages ──
    @discord.ui.button(label="Clean User Msgs", emoji="👤", style=discord.ButtonStyle.danger, row=0)
    async def user_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CleanUserModal())

    # ── 2. Delete by Link ──
    @discord.ui.button(label="Delete by Link", emoji="🔗", style=discord.ButtonStyle.primary, row=0)
    async def link_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DeleteLinkModal())

    # ── 3. Purge Channel ──
    @discord.ui.button(label="Purge Channel", emoji="📄", style=discord.ButtonStyle.secondary, row=0)
    async def purge_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PurgeChannelModal())

    # ── Cancel ──
    @discord.ui.button(label="Cancel", emoji="✖️", style=discord.ButtonStyle.secondary, row=1)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except discord.HTTPException:
            pass
        await interaction.response.send_message("❌ Clean panel cancelled.", ephemeral=True, delete_after=5)
        self.stop()


# ============================================================
#  MODAL 1 — Clean User Messages
# ============================================================

class CleanUserModal(discord.ui.Modal, title="👤 Clean User Messages"):
    """Delete messages from a specific user, even if they left."""

    user_input = discord.ui.TextInput(
        label="User ID or @Mention",
        placeholder="e.g. 123456789012345678",
        required=True,
        max_length=24,
    )
    scope_input = discord.ui.TextInput(
        label="Scope",
        placeholder="current = this channel  |  all = every channel",
        required=False,
        max_length=10,
        default="current",
    )
    limit_input = discord.ui.TextInput(
        label="Messages to scan (per channel)",
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
    )

    async def on_submit(self, interaction: discord.Interaction):
        # ── Parse User ID ──
        uid_str = self.user_input.value.strip()
        mention_match = re.match(r"<@!?(\d+)>", uid_str)
        if mention_match:
            uid_str = mention_match.group(1)

        if not uid_str.isdigit():
            await interaction.response.send_message(
                f"❌ Invalid User ID: `{uid_str}`.", ephemeral=True
            )
            return

        user_id = int(uid_str)

        # ── Parse scope ──
        scope = self.scope_input.value.strip().lower() or "current"
        scan_all = scope in ("all", "server", "global", "everywhere")

        # ── Parse limit ──
        limit_str = self.limit_input.value.strip() or "100"
        if not limit_str.isdigit():
            await interaction.response.send_message(
                f"❌ Invalid limit: `{limit_str}`.", ephemeral=True
            )
            return
        scan_limit = max(1, min(int(limit_str), 1000))

        reason = self.reason_input.value.strip() or "No reason provided"

        # ── Resolve user display ──
        try:
            user = await interaction.client.fetch_user(user_id)
            user_display = f"{user} (`{user_id}`)"
        except Exception:
            user_display = f"Unknown User (`{user_id}`)"

        # ── Confirmation embed ──
        scope_display = "All channels" if scan_all else f"#{interaction.channel.name}"

        confirm_embed = discord.Embed(
            title="⚠️  Confirm User Clean",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Delete all messages from this user?\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR_WARN,
            timestamp=datetime.now(timezone.utc),
        )
        confirm_embed.add_field(name="👤 Target", value=user_display, inline=True)
        confirm_embed.add_field(name="📍 Scope", value=scope_display, inline=True)
        confirm_embed.add_field(name="🔍 Scan Limit", value=f"{scan_limit}/channel", inline=True)
        confirm_embed.add_field(name="📝 Reason", value=reason, inline=False)
        confirm_embed.set_footer(text=FOOTER_TEXT)

        view = UserCleanConfirmView(
            user_id=user_id,
            user_display=user_display,
            scan_all=scan_all,
            scan_limit=scan_limit,
            reason=reason,
            moderator=interaction.user,
            source_channel=interaction.channel,
        )
        await interaction.response.send_message(embed=confirm_embed, view=view, ephemeral=True)


# ============================================================
#  MODAL 2 — Delete by Link
# ============================================================

class DeleteLinkModal(discord.ui.Modal, title="🔗 Delete by Message Link"):
    """Paste message link(s) to delete them."""

    links_input = discord.ui.TextInput(
        label="Message Link(s)",
        placeholder="Paste one or more Discord message links (one per line)",
        required=True,
        max_length=1000,
        style=discord.TextStyle.paragraph,
    )
    reason_input = discord.ui.TextInput(
        label="Reason (for logging)",
        placeholder="e.g. Inappropriate content",
        required=False,
        max_length=256,
    )

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.links_input.value.strip()
        reason = self.reason_input.value.strip() or "No reason provided"

        # Parse all links
        matches = LINK_PATTERN.findall(raw)
        if not matches:
            await interaction.response.send_message(
                "❌ No valid Discord message links found.\n"
                "Format: `https://discord.com/channels/SERVER/CHANNEL/MESSAGE`",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        deleted = 0
        errors = []
        guild = interaction.guild

        for guild_id_str, channel_id_str, message_id_str in matches:
            ch_id = int(channel_id_str)
            msg_id = int(message_id_str)

            channel = guild.get_channel(ch_id)
            if channel is None:
                errors.append(f"Channel `{ch_id}` not found")
                continue

            try:
                msg = await channel.fetch_message(msg_id)
                await msg.delete()
                deleted += 1
            except discord.NotFound:
                errors.append(f"Message `{msg_id}` not found in #{channel.name}")
            except discord.Forbidden:
                errors.append(f"No permission in #{channel.name}")
            except discord.HTTPException as e:
                errors.append(f"#{channel.name}: {str(e)[:50]}")

        # ── Result ──
        result_embed = discord.Embed(
            title="✅  Link Delete Complete" if deleted > 0 else "⚠️  Link Delete Failed",
            color=EMBED_COLOR_SUCCESS if deleted > 0 else EMBED_COLOR_DANGER,
            timestamp=datetime.now(timezone.utc),
        )
        result_embed.add_field(name="🗑️ Deleted", value=str(deleted), inline=True)
        result_embed.add_field(name="🔗 Links Processed", value=str(len(matches)), inline=True)
        result_embed.add_field(name="🛡️ Moderator", value=interaction.user.mention, inline=True)
        result_embed.add_field(name="📝 Reason", value=reason, inline=False)

        if errors:
            error_text = "\n".join(errors[:5])
            if len(errors) > 5:
                error_text += f"\n... +{len(errors) - 5} more"
            result_embed.add_field(name="⚠️ Errors", value=f"```{error_text}```", inline=False)

        result_embed.set_footer(text=FOOTER_TEXT)
        await interaction.followup.send(embed=result_embed, ephemeral=True)

        # ── Log ──
        cog = interaction.client.get_cog("CleanPanel")
        if cog:
            await cog.send_clean_log(
                guild=guild,
                moderator=interaction.user,
                action=f"Link Delete — {deleted} message(s) deleted",
                reason=reason,
            )


# ============================================================
#  MODAL 3 — Purge Channel
# ============================================================

class PurgeChannelModal(discord.ui.Modal, title="📄 Purge Channel"):
    """Bulk delete messages in the current channel."""

    amount_input = discord.ui.TextInput(
        label="Number of messages to delete",
        placeholder="Default: 100 (max 500)",
        required=False,
        max_length=4,
        default="100",
    )
    reason_input = discord.ui.TextInput(
        label="Reason (for logging)",
        placeholder="e.g. Channel cleanup",
        required=False,
        max_length=256,
    )

    async def on_submit(self, interaction: discord.Interaction):
        amount_str = self.amount_input.value.strip() or "100"
        reason = self.reason_input.value.strip() or "No reason provided"

        if not amount_str.isdigit():
            await interaction.response.send_message(
                f"❌ Invalid number: `{amount_str}`.", ephemeral=True
            )
            return

        amount = max(1, min(int(amount_str), 500))

        await interaction.response.defer(ephemeral=True)

        try:
            deleted = await interaction.channel.purge(limit=amount)

            result_embed = discord.Embed(
                title="🧹  Channel Purged",
                description=(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Deleted **{len(deleted)}** messages from {interaction.channel.mention}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ),
                color=EMBED_COLOR_SUCCESS,
                timestamp=datetime.now(timezone.utc),
            )
            result_embed.add_field(name="🛡️ Moderator", value=interaction.user.mention, inline=True)
            result_embed.add_field(name="📝 Reason", value=reason, inline=True)
            result_embed.set_footer(text=FOOTER_TEXT)

            # Send in channel (visible to all), auto-delete after 8 seconds
            temp = await interaction.channel.send(embed=result_embed)
            await temp.delete(delay=8)

            await interaction.followup.send(f"✅ Purged **{len(deleted)}** messages.", ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to delete messages in this channel.", ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Purge failed: {e}", ephemeral=True)

        # ── Log ──
        cog = interaction.client.get_cog("CleanPanel")
        if cog:
            await cog.send_clean_log(
                guild=interaction.guild,
                moderator=interaction.user,
                action=f"Channel Purge — {len(deleted)} messages in #{interaction.channel.name}",
                reason=reason,
            )


# ============================================================
#  CONFIRMATION VIEW — User Clean
# ============================================================

class UserCleanConfirmView(discord.ui.View):
    """Confirm or cancel user message cleanup."""

    def __init__(self, user_id, user_display, scan_all, scan_limit, reason, moderator, source_channel):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.user_display = user_display
        self.scan_all = scan_all
        self.scan_limit = scan_limit
        self.reason = reason
        self.moderator = moderator
        self.source_channel = source_channel

    @discord.ui.button(label="Confirm", emoji="✅", style=discord.ButtonStyle.danger, row=0)
    async def confirm_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        # Run the cleanup
        cog = interaction.client.get_cog("CleanPanel")
        if cog:
            await cog.execute_user_clean(
                channel=self.source_channel,
                user_id=self.user_id,
                user_display=self.user_display,
                scan_all=self.scan_all,
                scan_limit=self.scan_limit,
                reason=self.reason,
                moderator=self.moderator,
                guild=interaction.guild,
            )

    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary, row=0)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="❌ Cancelled.", embed=None, view=None)


# ============================================================
#  COG
# ============================================================

class CleanPanel(commands.Cog):
    """Interactive Clean Panel — user, link, and channel cleaning."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ────────────────────────────────────────────────
    #  PREFIX COMMAND: !clean
    # ────────────────────────────────────────────────

    @commands.command(name="clean", aliases=["purge", "clear"])
    @commands.has_permissions(manage_messages=True)
    async def clean_command(self, ctx):
        """Open the interactive clean panel."""

        panel_embed = discord.Embed(
            title="🧹  Clean Panel",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Choose a cleanup mode below.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR,
            timestamp=datetime.now(timezone.utc),
        )
        panel_embed.add_field(
            name="👤 Clean User Msgs",
            value="Delete messages by User ID\n(works even if they left)",
            inline=True,
        )
        panel_embed.add_field(
            name="🔗 Delete by Link",
            value="Paste message link(s)\nto delete specific messages",
            inline=True,
        )
        panel_embed.add_field(
            name="📄 Purge Channel",
            value="Bulk delete N messages\nin this channel",
            inline=True,
        )
        panel_embed.set_footer(text=FOOTER_TEXT)

        view = CleanPanelView(author_id=ctx.author.id)
        await ctx.reply(embed=panel_embed, view=view, mention_author=False)

    @clean_command.error
    async def clean_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "❌ You need **Manage Messages** permission.", delete_after=8, mention_author=False
            )

    # ────────────────────────────────────────────────
    #  EXECUTE USER CLEAN
    # ────────────────────────────────────────────────

    async def execute_user_clean(self, channel, user_id, user_display, scan_all,
                                  scan_limit, reason, moderator, guild):
        """Delete messages from a user — current channel or all channels."""

        start_time = time.monotonic()
        total_deleted = 0
        bulk_cutoff = datetime.now(timezone.utc) - timedelta(days=14)

        if scan_all:
            # ── All channels ──
            text_channels = [
                ch for ch in guild.text_channels
                if ch.permissions_for(guild.me).read_message_history
                and ch.permissions_for(guild.me).manage_messages
            ]

            progress_embed = discord.Embed(
                title="🔄  Cleaning — In Progress",
                description=f"Target: {user_display}",
                color=EMBED_COLOR_PROGRESS,
                timestamp=datetime.now(timezone.utc),
            )
            progress_embed.add_field(name="📂 Channels", value=f"0 / {len(text_channels)}", inline=True)
            progress_embed.add_field(name="🗑️ Deleted", value="0", inline=True)
            progress_embed.add_field(name="📍 Status", value="Starting...", inline=True)
            progress_embed.set_footer(text=FOOTER_TEXT)
            progress_msg = await channel.send(embed=progress_embed)

            for i, ch in enumerate(text_channels, 1):
                ch_deleted = await self._clean_channel(ch, user_id, scan_limit, bulk_cutoff)
                total_deleted += ch_deleted

                # Update every 3 channels
                if i % 3 == 0 or i == len(text_channels):
                    progress_embed.set_field_at(0, name="📂 Channels", value=f"{i} / {len(text_channels)}", inline=True)
                    progress_embed.set_field_at(1, name="🗑️ Deleted", value=str(total_deleted), inline=True)
                    progress_embed.set_field_at(2, name="📍 Status",
                                                 value="Finishing..." if i == len(text_channels) else f"#{ch.name}",
                                                 inline=True)
                    try:
                        await progress_msg.edit(embed=progress_embed)
                    except discord.HTTPException:
                        pass

            channels_scanned = len(text_channels)
        else:
            # ── Current channel only ──
            total_deleted = await self._clean_channel(channel, user_id, scan_limit, bulk_cutoff)
            channels_scanned = 1
            progress_msg = None

        # ── Completion ──
        elapsed = time.monotonic() - start_time
        secs = int(elapsed)
        mins, secs = divmod(secs, 60)
        time_display = f"{mins}m {secs}s" if mins else f"{secs}s"

        done_embed = discord.Embed(
            title="✅  User Clean — Complete",
            description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            color=EMBED_COLOR_SUCCESS,
            timestamp=datetime.now(timezone.utc),
        )
        done_embed.add_field(name="👤 Target", value=user_display, inline=True)
        done_embed.add_field(name="🛡️ Moderator", value=moderator.mention, inline=True)
        done_embed.add_field(name="🗑️ Deleted", value=str(total_deleted), inline=True)
        done_embed.add_field(name="📂 Channels", value=str(channels_scanned), inline=True)
        done_embed.add_field(name="⏱️ Time", value=time_display, inline=True)
        done_embed.add_field(name="📝 Reason", value=reason, inline=True)
        done_embed.set_footer(text=FOOTER_TEXT)

        if progress_msg:
            try:
                await progress_msg.edit(embed=done_embed)
            except discord.HTTPException:
                await channel.send(embed=done_embed)
        else:
            temp = await channel.send(embed=done_embed)
            await temp.delete(delay=15)

        # ── Log ──
        scope_str = f"{channels_scanned} channels" if scan_all else f"#{channel.name}"
        await self.send_clean_log(
            guild=guild,
            moderator=moderator,
            action=f"User Clean — {total_deleted} msgs from {user_display} in {scope_str}",
            reason=reason,
        )

    async def _clean_channel(self, channel, user_id, scan_limit, bulk_cutoff):
        """Delete all messages from user_id in a single channel. Returns count deleted."""
        deleted = 0

        try:
            recent = []
            old = []

            async for msg in channel.history(limit=scan_limit):
                if msg.author.id == user_id:
                    if msg.created_at.replace(tzinfo=timezone.utc) > bulk_cutoff:
                        recent.append(msg)
                    else:
                        old.append(msg)

            # Bulk delete recent (batches of 100)
            for i in range(0, len(recent), 100):
                batch = recent[i:i+100]
                if len(batch) == 1:
                    try:
                        await batch[0].delete()
                        deleted += 1
                    except discord.HTTPException:
                        pass
                elif len(batch) > 1:
                    try:
                        await channel.delete_messages(batch)
                        deleted += len(batch)
                    except discord.HTTPException:
                        for msg in batch:
                            try:
                                await msg.delete()
                                deleted += 1
                            except discord.HTTPException:
                                pass
                            await asyncio.sleep(0.3)

            # Old messages — individual delete
            for msg in old:
                try:
                    await msg.delete()
                    deleted += 1
                except discord.HTTPException:
                    pass
                await asyncio.sleep(0.5)

        except (discord.Forbidden, discord.HTTPException):
            pass

        return deleted

    # ────────────────────────────────────────────────
    #  MOD LOG
    # ────────────────────────────────────────────────

    async def send_clean_log(self, guild, moderator, action, reason):
        """Send a clean log to the mod-log channel."""
        try:
            from Bot import BAN_LOG_CHANNEL_ID
        except ImportError:
            return

        if BAN_LOG_CHANNEL_ID == 0:
            return

        channel = self.bot.get_channel(BAN_LOG_CHANNEL_ID)
        if channel is None:
            return

        log_embed = discord.Embed(
            title="🧹  Clean Log",
            description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            color=EMBED_COLOR_PROGRESS,
            timestamp=datetime.now(timezone.utc),
        )
        log_embed.add_field(name="🛡️ Moderator", value=f"{moderator} (`{moderator.id}`)", inline=True)
        log_embed.add_field(name="📋 Action", value=action, inline=False)
        log_embed.add_field(name="📝 Reason", value=reason, inline=False)
        log_embed.set_footer(text=FOOTER_TEXT)

        try:
            await channel.send(embed=log_embed)
        except discord.HTTPException:
            pass


# ============================================================
#  COG SETUP
# ============================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(CleanPanel(bot))
    print("✅ Clean Panel cog registered.")
