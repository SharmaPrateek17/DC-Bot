"""
╔══════════════════════════════════════════════════════════════╗
║         ✦  Modern Command Center (Prefix Command)           ║
║   Premium interactive help panel with dropdown navigation    ║
╚══════════════════════════════════════════════════════════════╝

Commands:
  !commandcenter  — Opens the premium help panel
  !cc             — Alias for !commandcenter
"""

import discord
from discord.ext import commands
from datetime import datetime, timezone


# =========================
# 🎨 THEME
# =========================

ACCENT          = 0x7C3AED   # Vibrant purple
COLOR_MOD       = 0xEF4444   # Red
COLOR_EVENTS    = 0x10B981   # Emerald
COLOR_UTILITY   = 0x3B82F6   # Blue
COLOR_ALL       = 0x8B5CF6   # Indigo
BOT_NAME        = "Sarkar Bot"
BOT_VERSION     = "2.5.0"
FOOTER          = f"{BOT_NAME}  ✦  v{BOT_VERSION}"


# ============================================================
#  COMMAND DATA
# ============================================================
# Each entry: (name, description, usage)

COMMANDS = {
    "moderation": {
        "title": "🛡️  Moderation",
        "color": COLOR_MOD,
        "commands": [
            ("!ban",          "Open the interactive ban panel",               "!ban"),
            ("!forceban",     "Ban a user by ID (even if they left)",         '!forceban 123 "spam" 7d none'),
            ("!clean",        "Interactive clean panel (user/link/purge)",     "!clean"),
            ("!deepclean",    "Remove a user's msgs from all channels",       "!deepclean"),
        ],
    },
    "events": {
        "title": "🎉  Events & Registration",
        "color": COLOR_EVENTS,
        "commands": [
            ("!events",        "Full event schedule table",                   "!events"),
            ("!status",        "Live sessions & upcoming events",             "!status"),
            ("!registrations", "View confirmed & waiting lists",              "!registrations"),
            ("!start",         "Interactive session creator",                 "!start"),
            ("!close",         "Force-close an active session",               "!close"),
            ("!raid",          "Trigger a Family Raid alert",                 "!raid"),
            ("!robbery",       "Open a Store Robbery signup",                 "!robbery"),
        ],
    },
    "utility": {
        "title": "⚙️  Utility & Tools",
        "color": COLOR_UTILITY,
        "commands": [
            ("!announcement",  "Rich text announcement editor",              "!announcement"),
            ("!pager",         "Send pager messages to the family",           "!pager"),
            ("!leaderboard",   "Top 10 most active members",                 "!leaderboard"),
            ("!quote",         "Random motivational quote",                   "!quote"),
        ],
    },
}


# ============================================================
#  EMBED BUILDERS
# ============================================================

def _footer(embed: discord.Embed, extra: str = ""):
    """Apply consistent footer styling."""
    text = f"{FOOTER}  •  {extra}" if extra else FOOTER
    embed.set_footer(text=text)
    embed.timestamp = datetime.now(timezone.utc)


def build_home(ctx_or_guild, gif_url=None):
    """Build the home / dashboard embed."""

    # Dynamic stats
    guild = ctx_or_guild.guild if hasattr(ctx_or_guild, 'guild') else ctx_or_guild
    member_count = guild.member_count if guild else "?"

    # Uptime
    try:
        from Bot import bot_start_time, UK_TZ
        if bot_start_time:
            delta = datetime.now(UK_TZ) - bot_start_time
            hours, rem = divmod(int(delta.total_seconds()), 3600)
            minutes, _ = divmod(rem, 60)
            uptime = f"{hours}h {minutes}m" if hours else f"{minutes}m"
        else:
            uptime = "Just started"
    except Exception:
        uptime = "—"

    try:
        from Bot import active_sessions
        sessions = len(active_sessions)
    except Exception:
        sessions = 0

    em = discord.Embed(
        title="✦  SARKAR COMMAND CENTER  ✦",
        description=(
            "Your all-in-one family bot for events, "
            "moderation, and server management.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=ACCENT,
    )

    # ── GIF as banner (top of embed) ──
    if gif_url:
        em.set_image(url=gif_url)

    # ── Stats row ──
    em.add_field(name="👥  Members", value=f"```{member_count}```", inline=True)
    em.add_field(name="📡  Sessions", value=f"```{sessions}```", inline=True)
    em.add_field(name="⏱️  Uptime", value=f"```{uptime}```", inline=True)

    # ── Category overview ──
    em.add_field(
        name="📂  Browse Categories",
        value=(
            "> 🛡️ **Moderation** — Bans, cleanup, purge\n"
            "> 🎉 **Events** — Schedule, sessions, raids\n"
            "> ⚙️ **Utility** — Announcements, pager, fun\n"
            "> 📋 **All Commands** — Full command list"
        ),
        inline=False,
    )

    # ── Quick tips ──
    em.add_field(
        name="💡  Quick Tips",
        value=(
            "Use `!ban` for the interactive ban system\n"
            "React with 🎟️ on event embeds to register\n"
            "All commands use the `!` prefix"
        ),
        inline=False,
    )

    _footer(em, "Select a category below")
    return em


def build_category(key: str) -> discord.Embed:
    """Build an embed for a specific command category."""
    cat = COMMANDS[key]

    em = discord.Embed(
        title=cat["title"],
        description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=cat["color"],
    )

    for name, desc, usage in cat["commands"]:
        em.add_field(
            name=f"`{name}`",
            value=f"{desc}\n> `{usage}`",
            inline=False,
        )

    _footer(em, cat["title"].split("  ", 1)[-1])
    return em


def build_all_commands() -> discord.Embed:
    """Build a compact embed listing every command."""
    em = discord.Embed(
        title="📋  All Commands",
        description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=COLOR_ALL,
    )

    for key, cat in COMMANDS.items():
        lines = []
        for name, desc, usage in cat["commands"]:
            lines.append(f"`{name}` — {desc}")
        em.add_field(
            name=cat["title"],
            value="\n".join(lines),
            inline=False,
        )

    em.add_field(
        name="💡  Quick Tips",
        value=(
            "All commands use the `!` prefix\n"
            "Some commands require specific permissions\n"
            "Use `!help` or `!cc` to reopen this panel"
        ),
        inline=False,
    )

    _footer(em, "All Commands")
    return em


# ============================================================
#  VIEW (Dropdown + Buttons)
# ============================================================

class CommandCenterView(discord.ui.View):
    """Interactive Command Center with select menu and nav buttons."""

    def __init__(self, author_id: int, gif_url=None, ctx=None):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.gif_url = gif_url
        self.ctx = ctx
        self.current = "home"
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Only the command user can navigate.", ephemeral=True)
            return False
        return True

    # ── Dropdown ──
    @discord.ui.select(
        placeholder="📂  Select a category...",
        options=[
            discord.SelectOption(label="Home",          value="home",       emoji="🏠", description="Dashboard & live stats"),
            discord.SelectOption(label="Moderation",    value="moderation", emoji="🛡️", description="Ban, cleanup, purge"),
            discord.SelectOption(label="Events",        value="events",     emoji="🎉", description="Schedule, sessions, raids"),
            discord.SelectOption(label="Utility",       value="utility",    emoji="⚙️", description="Announcements, pager, fun"),
            discord.SelectOption(label="All Commands",  value="all",        emoji="📋", description="Every command in one view"),
        ],
        row=0,
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.current = select.values[0]
        embed = self._get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    # ── Navigation buttons ──
    @discord.ui.button(label="Home", emoji="🏠", style=discord.ButtonStyle.primary, row=1)
    async def home_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = "home"
        embed = self._get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Moderation", emoji="🛡️", style=discord.ButtonStyle.danger, row=1)
    async def mod_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = "moderation"
        embed = self._get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Events", emoji="🎉", style=discord.ButtonStyle.success, row=1)
    async def events_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = "events"
        embed = self._get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Utility", emoji="⚙️", style=discord.ButtonStyle.secondary, row=1)
    async def util_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = "utility"
        embed = self._get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Close", emoji="✖️", style=discord.ButtonStyle.danger, row=2)
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except discord.HTTPException:
            pass
        self.stop()

    # ── Helper ──
    def _get_embed(self) -> discord.Embed:
        if self.current == "home":
            return build_home(self.ctx, self.gif_url)
        elif self.current == "all":
            return build_all_commands()
        else:
            return build_category(self.current)

    async def on_timeout(self):
        """Grey out all components when the view times out."""
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                em = self._get_embed()
                em.set_footer(text="⏰ Menu timed out  •  Use !cc to reopen")
                em.color = 0x6B7280
                await self.message.edit(embed=em, view=self)
            except (discord.NotFound, discord.HTTPException):
                pass


# ============================================================
#  COG
# ============================================================

class CommandCenter(commands.Cog):
    """Premium interactive Command Center."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _get_gif(self):
        """Load the HELP_GIF url from config."""
        try:
            from Bot import get_bot_gif
            return get_bot_gif("HELP_GIF")
        except Exception:
            return None

    # ── !commandcenter / !cc ──
    @commands.command(name="commandcenter", aliases=["cc"])
    async def commandcenter_cmd(self, ctx):
        """Open the Sarkar Command Center — premium help panel."""
        gif = self._get_gif()
        embed = build_home(ctx, gif)
        view = CommandCenterView(author_id=ctx.author.id, gif_url=gif, ctx=ctx)
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg


# ============================================================
#  COG SETUP
# ============================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(CommandCenter(bot))
    print("✅ Command Center cog registered.")
