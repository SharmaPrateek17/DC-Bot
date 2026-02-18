import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound
import asyncio
import random
import os
from datetime import datetime, timedelta
from collections import Counter

import pytz
from dotenv import load_dotenv

load_dotenv()

# =========================
# 🔹 PASTE YOUR IDs HERE
# =========================

channel_id = 1473346234763706549   # <-- Replace with your channel ID
allowed_role_id = 1467869329256091648  # <-- Replace with your role ID

# =========================
# 🎨 THEME
# =========================

EMBED_COLOR = 0x7C3AED        # Vibrant purple
EMBED_COLOR_SUCCESS = 0x10B981 # Emerald green
EMBED_COLOR_WARN = 0xF59E0B   # Amber
EMBED_COLOR_CLOSE = 0xEF4444  # Red
FOOTER_TEXT = "Informal Dedication Bot ✦"

# Registration emoji — users react with this to register
REGISTER_EMOJI = "✅"

# =========================
# 🎲 FUN DATA
# =========================

SLOT_EMOJIS = ["🔥", "⭐", "🎯", "💎", "🚀", "🏆", "💫", "✨", "🎉", "👑"]

SLOT_MESSAGES = [
    "claimed a slot! LET'S GO!",
    "is in the building! 🏠",
    "dropped in like a BOSS! 😎",
    "showed up and showed OUT!",
    "just made it legendary! 🐐",
    "entered the arena! ⚔️",
    "is here to DOMINATE!",
    "brought the ENERGY! ⚡",
    "just raised the bar! 📈",
    "locked in! No cap! 🔒",
]

MOTIVATIONAL_QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Stay hungry, stay foolish.", "Steve Jobs"),
    ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
    ("Success is not final, failure is not fatal.", "Winston Churchill"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("You are never too old to set another goal or to dream a new dream.", "C.S. Lewis"),
    ("Dream big and dare to fail.", "Norman Vaughan"),
    ("Hard work beats talent when talent doesn't work hard.", "Tim Notke"),
    ("Be the change that you wish to see in the world.", "Mahatma Gandhi"),
    ("What you get by achieving your goals is not as important as what you become.", "Zig Ziglar"),
    ("Discipline is the bridge between goals and accomplishment.", "Jim Rohn"),
    ("Wake up with determination, go to bed with satisfaction.", "Unknown"),
]

SESSION_OPEN_TITLES = [
    "🚪 The Gates Are OPEN!",
    "🔓 Session UNLOCKED!",
    "⚡ IT'S GO TIME!",
    "🎰 The Slots Are Live!",
    "🏟️ Arena Is Now OPEN!",
]

SESSION_CLOSE_TITLES = [
    "🔒 Session LOCKED!",
    "🚪 Gates CLOSED!",
    "⏰ Time's UP!",
    "🏁 That's a WRAP!",
]

# =========================
# ⚙️ BOT SETUP
# =========================

IST = pytz.timezone("Asia/Kolkata")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

active_session = False
participants = {}           # {user_id: slot_number}
session_start_time = None
session_message_id = None   # The message users react to
all_time_leaderboard = Counter()  # {user_id: count}


# =========================
# 📦 HELPER — BUILD EMBEDS
# =========================

def make_embed(title, description, color=EMBED_COLOR, fields=None, thumbnail=None):
    """Build a styled embed quickly."""
    em = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(IST),
    )
    em.set_footer(text=FOOTER_TEXT)
    if thumbnail:
        em.set_thumbnail(url=thumbnail)
    if fields:
        for name, value, inline in fields:
            em.add_field(name=name, value=value, inline=inline)
    return em


def build_live_embed(title_text):
    """Build the session embed showing current slot status."""
    slots_taken = len(participants)
    slots_left = 10 - slots_taken
    progress = "█" * slots_taken + "░" * slots_left

    # Build current registrant list
    if participants:
        lines = []
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for uid, slot in sorted(participants.items(), key=lambda x: x[1]):
            medal = medals.get(slot, f"**#{slot}**")
            emoji = SLOT_EMOJIS[slot - 1] if slot <= len(SLOT_EMOJIS) else "🎉"
            member = bot.get_guild(bot.get_channel(channel_id).guild.id).get_member(uid)
            name = member.display_name if member else f"User#{uid}"
            lines.append(f"{emoji} {medal} **{name}**")
        registrant_list = "\n".join(lines)
    else:
        registrant_list = "*No one yet… be the first!*"

    em = make_embed(
        title=title_text,
        description=(
            f"React with {REGISTER_EMOJI} below to **register!**\n"
            f"First **10** members get a slot.\n\n"
            f"```\n[{progress}] {slots_taken}/10 slots claimed\n```\n"
        ),
        color=EMBED_COLOR if slots_left > 0 else EMBED_COLOR_CLOSE,
        fields=[
            ("🎰 Slots Left", f"**{slots_left}**", True),
            ("⏳ Time Limit", "8 minutes", True),
            ("📍 Status", "🟢 OPEN" if slots_left > 0 else "🔴 FULL", True),
            ("📝 Registered", registrant_list, False),
        ],
    )
    return em


# =========================
# ⏰ HOURLY CHECK
# =========================
@tasks.loop(minutes=1)
async def hourly_check():
    global active_session, participants, session_start_time, session_message_id

    now = datetime.now(IST)

    # Session triggers at the start of every hour
    if now.minute == 0 and not active_session:
        channel = bot.get_channel(channel_id)
        if channel is None:
            return
        role = channel.guild.get_role(allowed_role_id)

        participants = {}
        active_session = True
        session_start_time = now

        # Unlock channel for role
        await channel.set_permissions(role, send_messages=True)

        title = random.choice(SESSION_OPEN_TITLES)
        em = build_live_embed(title)

        msg = await channel.send(embed=em)
        session_message_id = msg.id

        # Add the registration reaction for users to click
        await msg.add_reaction(REGISTER_EMOJI)

        print(f"📢 Session opened! Message ID: {session_message_id}")

        # Wait 8 minutes
        await asyncio.sleep(480)

        if active_session:
            await close_session(channel)


# =========================
# 🎯 REACTION-BASED REGISTRATION
# =========================
@bot.event
async def on_raw_reaction_add(payload):
    """Track reactions on the session message to register users."""
    global active_session, participants

    # Ignore bot's own reactions
    if payload.user_id == bot.user.id:
        return

    # Only care about the session message
    if not active_session or session_message_id is None:
        return
    if payload.message_id != session_message_id:
        return
    if payload.channel_id != channel_id:
        return

    # Only count the registration emoji
    if str(payload.emoji) != REGISTER_EMOJI:
        # Remove non-registration reactions
        channel = bot.get_channel(channel_id)
        msg = await channel.fetch_message(session_message_id)
        member = payload.member or channel.guild.get_member(payload.user_id)
        if member:
            try:
                await msg.remove_reaction(payload.emoji, member)
            except Exception:
                pass
        return

    # Already registered
    if payload.user_id in participants:
        return

    # Session full
    if len(participants) >= 10:
        return

    # ✅ Register the user!
    slot = len(participants) + 1
    participants[payload.user_id] = slot
    all_time_leaderboard[payload.user_id] += 1

    member = payload.member or bot.get_guild(payload.guild_id).get_member(payload.user_id)
    name = member.display_name if member else f"User#{payload.user_id}"
    fun_msg = random.choice(SLOT_MESSAGES)
    emoji = SLOT_EMOJIS[slot - 1] if slot <= len(SLOT_EMOJIS) else "🎉"

    print(f"   {emoji} Slot #{slot}: {name}")

    # Update the session embed live with the new registrant
    channel = bot.get_channel(channel_id)
    try:
        msg = await channel.fetch_message(session_message_id)
        updated_em = build_live_embed(msg.embeds[0].title if msg.embeds else "🎰 Registration Open!")
        await msg.edit(embed=updated_em)
    except Exception as e:
        print(f"⚠️ Could not update embed: {e}")

    # Send a quick confirmation in channel (auto-deletes after 5s)
    slots_left = 10 - slot
    confirm_em = make_embed(
        title=f"{emoji}  Slot #{slot} Claimed!",
        description=f"**{name}** {fun_msg}",
        color=EMBED_COLOR_SUCCESS,
        fields=[
            ("🎰 Slots Left", f"**{slots_left}**", True),
        ],
    )
    temp_msg = await channel.send(embed=confirm_em)
    # Auto-delete the confirmation after 5 seconds
    await asyncio.sleep(5)
    try:
        await temp_msg.delete()
    except discord.NotFound:
        pass

    # If 10 users → close immediately
    if slot >= 10:
        await close_session(channel)


# =========================
# 📨 MESSAGE HANDLER (commands only)
# =========================
@bot.event
async def on_message(message):
    # Always process commands
    await bot.process_commands(message)

    if message.author.bot:
        return
    if message.channel.id != channel_id:
        return
    # Skip command messages
    if message.content.startswith("!"):
        return

    # If session is active, tell them to react instead of typing
    if active_session:
        em = make_embed(
            title="👆  React to Register!",
            description=(
                f"Don't type — **react with {REGISTER_EMOJI}** on the session message above!\n"
                "That's how you claim a slot. 🎰"
            ),
            color=EMBED_COLOR_WARN,
        )
        reply = await message.reply(embed=em, mention_author=False)
        await asyncio.sleep(6)
        try:
            await reply.delete()
            await message.delete()
        except discord.NotFound:
            pass
        return

    # No session — channel is locked
    em = make_embed(
        title="🔴  Channel is Locked!",
        description=(
            "No active session right now.\n"
            "The channel **opens at the top of every hour**.\n\n"
            "Use `!status` to check when the next session starts!"
        ),
        color=EMBED_COLOR_WARN,
    )
    reply = await message.reply(embed=em, mention_author=False)
    await asyncio.sleep(8)
    try:
        await reply.delete()
    except discord.NotFound:
        pass


# =========================
# 🔒 CLOSE SESSION
# =========================
async def close_session(channel):
    global active_session, session_start_time, session_message_id

    active_session = False  # Stop accepting reactions immediately

    role = channel.guild.get_role(allowed_role_id)

    # Lock channel
    await channel.set_permissions(role, send_messages=False)

    title = random.choice(SESSION_CLOSE_TITLES)
    count = len(participants)
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    if participants:
        lines = []
        for uid, slot in sorted(participants.items(), key=lambda x: x[1]):
            medal = medals.get(slot, f"**#{slot}**")
            member = channel.guild.get_member(uid)
            name = member.display_name if member else f"User#{uid}"
            lines.append(f"{medal} **{name}**")
        user_list = "\n".join(lines)
    else:
        user_list = "*No one showed up… maybe next hour!* 😢"

    elapsed = ""
    if session_start_time:
        delta = datetime.now(IST) - session_start_time
        mins = int(delta.total_seconds() // 60)
        secs = int(delta.total_seconds() % 60)
        elapsed = f"{mins}m {secs}s"

    em = make_embed(
        title=title,
        description=f"The session is now **closed**.\n\n**{count}/10** slots were claimed.",
        color=EMBED_COLOR_CLOSE,
        fields=[
            ("👥 Participants", user_list, False),
            ("⏱️ Duration", elapsed or "—", True),
            ("📊 Total Slots", f"{count} / 10", True),
        ],
    )

    await channel.send(embed=em)

    # 🧹 Clean up: wait, then purge ALL messages from the session
    await asyncio.sleep(10)

    try:
        deleted = await channel.purge(
            limit=200,
            check=lambda m: True,
        )
        print(f"🧹 Purged {len(deleted)} messages from #{channel.name}")
    except discord.Forbidden:
        print("⚠️ Missing permissions to purge messages!")
    except Exception as e:
        print(f"⚠️ Purge error: {e}")

    # Post a clean final summary that stays
    if participants:
        summary_lines = []
        for uid, slot in sorted(participants.items(), key=lambda x: x[1]):
            medal = medals.get(slot, f"#{slot}")
            member = channel.guild.get_member(uid)
            name = member.display_name if member else f"User#{uid}"
            summary_lines.append(f"{medal} {name}")
        summary_text = "\n".join(summary_lines)
    else:
        summary_text = "No participants."

    clean_em = make_embed(
        title="📋  Session Summary",
        description=(
            f"**{count}** member(s) registered.\n"
            f"Duration: **{elapsed or '—'}**\n\n"
            f"{summary_text}\n\n"
            "*Next session opens at the top of the next hour.* ⏳"
        ),
        color=EMBED_COLOR,
    )
    await channel.send(embed=clean_em)

    session_start_time = None
    session_message_id = None


# ============================================================
# 🎮  INTERACTIVE COMMANDS
# ============================================================

# ---------- !help ----------
@bot.command(name="help")
async def help_cmd(ctx):
    """Custom styled help embed."""
    em = make_embed(
        title="📖  Command Center",
        description="Here's everything I can do!",
        color=EMBED_COLOR,
        fields=[
            ("!status", "Check if a session is running, slots left, time remaining.", False),
            ("!leaderboard", "See the all-time most dedicated members. 🏆", False),
            ("!quote", "Get a random motivational quote to fuel your day. 💬", False),
            ("!help", "Show this help message.", False),
        ],
    )
    await ctx.reply(embed=em, mention_author=False)


# ---------- !status ----------
@bot.command(name="status")
async def status_cmd(ctx):
    """Show current session status."""
    if active_session:
        slots_taken = len(participants)
        slots_left = 10 - slots_taken
        progress = "█" * slots_taken + "░" * slots_left

        elapsed = ""
        remaining = ""
        if session_start_time:
            delta = datetime.now(IST) - session_start_time
            mins_passed = int(delta.total_seconds() // 60)
            secs_passed = int(delta.total_seconds() % 60)
            elapsed = f"{mins_passed}m {secs_passed}s"
            time_left = max(0, 480 - int(delta.total_seconds()))
            remaining = f"{time_left // 60}m {time_left % 60}s"

        em = make_embed(
            title="🟢  Session is LIVE!",
            description=(
                f"```\n[{progress}] {slots_taken}/10 slots claimed\n```\n"
                f"React with {REGISTER_EMOJI} on the session message to register!"
            ),
            color=EMBED_COLOR_SUCCESS,
            fields=[
                ("🎰 Slots Left", f"**{slots_left}**", True),
                ("⏱️ Elapsed", elapsed or "—", True),
                ("⏳ Remaining", remaining or "—", True),
            ],
        )
    else:
        now = datetime.now(IST)
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        diff = next_hour - now
        mins = int(diff.total_seconds() // 60)

        em = make_embed(
            title="🔴  No Active Session",
            description=(
                f"Next session opens in **~{mins} minutes**.\n"
                "Hang tight! ⏳"
            ),
            color=EMBED_COLOR_WARN,
        )

    await ctx.reply(embed=em, mention_author=False)


# ---------- !leaderboard ----------
@bot.command(name="leaderboard")
async def leaderboard_cmd(ctx):
    """All-time leaderboard (in-memory, resets on bot restart)."""
    if not all_time_leaderboard:
        em = make_embed(
            title="🏆  Leaderboard",
            description="No data yet! Participate in a session to get on the board.",
            color=EMBED_COLOR_WARN,
        )
        await ctx.reply(embed=em, mention_author=False)
        return

    top = all_time_leaderboard.most_common(10)
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = []
    for rank, (uid, count) in enumerate(top, start=1):
        medal = medals.get(rank, f"**#{rank}**")
        lines.append(f"{medal} <@{uid}> — **{count}** session(s)")

    em = make_embed(
        title="🏆  All-Time Leaderboard",
        description="\n".join(lines),
        color=EMBED_COLOR,
    )
    await ctx.reply(embed=em, mention_author=False)


# ---------- !quote ----------
@bot.command(name="quote")
async def quote_cmd(ctx):
    """Send a random motivational quote."""
    text, author = random.choice(MOTIVATIONAL_QUOTES)
    em = make_embed(
        title="💬  Quote of the Moment",
        description=f"*\"{text}\"*\n\n— **{author}**",
        color=EMBED_COLOR_SUCCESS,
    )
    await ctx.reply(embed=em, mention_author=False)


# ============================================================
# ❌  WRONG COMMAND HANDLER
# ============================================================
@bot.event
async def on_command_error(ctx, error):
    """If someone types a wrong !command, show the valid commands."""
    if isinstance(error, CommandNotFound):
        wrong_cmd = ctx.message.content.split()[0]
        em = make_embed(
            title="❌  Unknown Command!",
            description=(
                f"`{wrong_cmd}` is not a valid command.\n\n"
                "Here are the commands I understand:"
            ),
            color=EMBED_COLOR_CLOSE,
            fields=[
                ("!help", "Show all commands & how to use them.", False),
                ("!status", "Check if a session is running, slots left, time remaining.", False),
                ("!leaderboard", "See the all-time most dedicated members. 🏆", False),
                ("!quote", "Get a random motivational quote. 💬", False),
            ],
        )
        await ctx.reply(embed=em, mention_author=False)
    else:
        raise error


# =========================
# 🚀 WHEN BOT STARTS
# =========================
@bot.event
async def on_ready():
    print(f"✅ Bot is ready! Logged in as {bot.user}")
    print(f"📡 Watching channel {channel_id}")
    print(f"🔁 Hourly check loop started")
    hourly_check.start()


# =========================
# 🔑 START BOT (token from .env)
# =========================
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("❌ DISCORD_TOKEN not found in .env file!")
bot.run(token)
