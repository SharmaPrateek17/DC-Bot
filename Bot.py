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
# 📅 EVENT SCHEDULE DATA (UK Time)
# =========================

# Format: (HH:MM, Event Name, Optional Day List)
# Days: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
# If days is None, it triggers every day.

EVENT_LIST = [
    # Store Robbery (Informal Signup) - Every Hour at the top of the hour
    ("00:00", "Store Robbery (Informal Signup)", None),
    ("01:00", "Store Robbery (Informal Signup)", None),
    ("02:00", "Store Robbery (Informal Signup)", None),
    ("03:00", "Store Robbery (Informal Signup)", None),
    ("04:00", "Store Robbery (Informal Signup)", None),
    ("05:00", "Store Robbery (Informal Signup)", None),
    ("06:00", "Store Robbery (Informal Signup)", None),
    ("07:00", "Store Robbery (Informal Signup)", None),
    ("08:00", "Store Robbery (Informal Signup)", None),
    ("09:00", "Store Robbery (Informal Signup)", None),
    ("10:00", "Store Robbery (Informal Signup)", None),
    ("11:00", "Store Robbery (Informal Signup)", None),
    ("12:00", "Store Robbery (Informal Signup)", None),
    ("13:00", "Store Robbery (Informal Signup)", None),
    ("14:00", "Store Robbery (Informal Signup)", None),
    ("15:00", "Store Robbery (Informal Signup)", None),
    ("16:00", "Store Robbery (Informal Signup)", None),
    ("17:00", "Store Robbery (Informal Signup)", None),
    ("18:00", "Store Robbery (Informal Signup)", None),
    ("19:00", "Store Robbery (Informal Signup)", None),
    ("20:00", "Store Robbery (Informal Signup)", None),
    ("21:00", "Store Robbery (Informal Signup)", None),
    ("22:00", "Store Robbery (Informal Signup)", None),
    ("23:00", "Store Robbery (Informal Signup)", None),
    # Scheduled Daily Events
    ("01:05", "Business War", None),
    ("01:10", "Harbor", None),
    ("02:20", "Hotel Takeover", None),
    ("03:20", "Weapons Factory", None),
    ("04:10", "Harbor", None),
    ("07:10", "Harbor", None),
    ("07:20", "Weapons Factory", None),
    ("10:00", "Drug Lab (10:00-23:00)", None),
    ("10:10", "Harbor", None),
    ("10:20", "Weapons Factory", None),
    ("13:10", "Harbor", None),
    ("14:20", "Foundry", None),
    ("16:10", "Harbor", None),
    ("17:15", "Mall (Registration at 17:15, Defense at 17:20, Attack at 17:25)", None),
    ("19:05", "Business War", None),
    ("19:10", "Harbor", None),
    ("20:15", "Vineyard", None),
    ("20:20", "Attacking Prison", [4]), # Friday Only
    ("20:20", "King Of Cayo Perico Island", [2, 6]), # Wednesday & Sunday Only
    ("20:30", "Leftover Components", None),
    ("20:50", "Rating Battle", None),
    ("21:30", "Aircraft Carrier", [6]), # Sunday Only
    ("17:30", "Bank Robbery (Registration at 17:30 for 21:30 event)", [0, 2, 5]), # Mon, Wed, Sat
    ("22:10", "Harbor", None),
    ("22:20", "Weapons Factory", None),
]

# =========================
# ⚙️ BOT SETUP
# =========================

UK_TZ = pytz.timezone("Europe/London")

GUN_LOSS_EVENTS = ["Business War", "Hotel Takeover", "Rating Battle"]
NO_GUN_LOSS_EVENTS = ["Harbor", "Foundry", "Mall", "Vineyard", "Weapons Factory"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

active_session = False
current_event_name = "Session"
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
        timestamp=datetime.now(UK_TZ),
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

    # Determine if gun loss applies
    warning_field = []
    is_dangerous = any(danger in current_event_name for danger in GUN_LOSS_EVENTS)
    if is_dangerous:
        warning_field = [("⚠️ Gear Warning", "You **LOSE** guns/ammo on death in this event (unless you have Prime Platinum).", False)]
    elif any(safe in current_event_name for safe in NO_GUN_LOSS_EVENTS):
        warning_field = [("✅ Gear Safe", "You **DO NOT** lose guns/ammo on death in this event.", False)]

    em = make_embed(
        title=title_text,
        description=(
            f"Registration for: **{current_event_name}**\n"
            f"React with {REGISTER_EMOJI} below to **register!**\n"
            f"First **10** members get a slot.\n\n"
            f"```\n[{progress}] {slots_taken}/10 slots claimed\n```\n"
        ),
        color=EMBED_COLOR if slots_left > 0 else EMBED_COLOR_CLOSE,
        fields=[
            ("🎰 Slots Left", f"**{slots_left}**", True),
            ("⏳ Time Limit", "8 minutes", True),
            ("📍 Status", "🟢 OPEN" if slots_left > 0 else "🔴 FULL", True),
        ] + warning_field + [
            ("📝 Registered", registrant_list, False),
        ],
    )
    return em


# =========================
# ⏰ EVENT SCHEDULER (Every Minute Check)
# =========================

async def open_poll(matching_events):
    """Handle the opening and timed closing of a registration session."""
    global active_session, participants, session_start_time, session_message_id, current_event_name
    
    channel = bot.get_channel(channel_id)
    if channel is None:
        return
    role = channel.guild.get_role(allowed_role_id)

    participants = {}
    active_session = True
    current_event_name = " & ".join(matching_events)
    session_start_time = datetime.now(UK_TZ)

    # Unlock channel for role
    await channel.set_permissions(role, send_messages=True)

    title = random.choice(SESSION_OPEN_TITLES)
    em = build_live_embed(title)

    msg = await channel.send(embed=em)
    session_message_id = msg.id

    # Add the registration reaction for users to click
    await msg.add_reaction(REGISTER_EMOJI)

    print(f"📢 Poll opened for {current_event_name}! (UK Time: {session_start_time.strftime('%H:%M')})")

    # Wait 8 minutes
    await asyncio.sleep(480)

    # Only auto-close if this specific session is still the active one
    if active_session and session_message_id == msg.id:
        await close_session(channel)


@tasks.loop(minutes=1)
async def event_scheduler():
    global active_session

    now = datetime.now(UK_TZ)
    current_time_str = now.strftime("%H:%M")
    current_day = now.weekday()

    # Find all events right now
    matching_events = []
    for time_str, name, days in EVENT_LIST:
        if time_str == current_time_str:
            if days is None or current_day in days:
                matching_events.append(name)

    if matching_events:
        if not active_session:
            # Start the poll in a background task so the scheduler loop can continue
            asyncio.create_task(open_poll(matching_events))
        else:
            event_names = ", ".join(matching_events)
            print(f"⚠️ Skipping scheduled events ({event_names}) - A session is already active.")


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

    # Send a quick confirmation in channel (auto-deletes after 15s)
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
    # Auto-delete the confirmation after 15 seconds
    await asyncio.sleep(15)
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
        delta = datetime.now(UK_TZ) - session_start_time
        mins = int(delta.total_seconds() // 60)
        secs = int(delta.total_seconds() % 60)
        elapsed = f"{mins}m {secs}s"

    em = make_embed(
        title=title,
        description=f"The registration for **{current_event_name}** is now **closed**.\n\n**{count}/10** slots were claimed.",
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
        title=f"📋  {current_event_name} Summary",
        description=(
            f"**{count}** member(s) registered.\n"
            f"Duration: **{elapsed or '—'}**\n\n"
            f"{summary_text}\n\n"
            f"*Next event reminder will trigger automatically.* ⏳"
        ),
        color=EMBED_COLOR,
    )
    await channel.send(embed=clean_em)

    session_start_time = None
    session_message_id = None
    current_event_name = "Session"


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
            ("!status", "Check if a session is running and see registrations.", False),
            ("!registrations", "List currently registered participants.", False),
            ("!events", "Show the full event schedule and gun rules. 📅", False),
            ("!leaderboard", "See the all-time most dedicated members. 🏆", False),
            ("!quote", "Get a random motivational quote to fuel your day. 💬", False),
            ("!clean [amount]", "Purge messages from the channel (Admin only). 🧹", False),
            ("!start", "Manually start a registration session (Admin only).", False),
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
            delta = datetime.now(UK_TZ) - session_start_time
            mins_passed = int(delta.total_seconds() // 60)
            secs_passed = int(delta.total_seconds() % 60)
            elapsed = f"{mins_passed}m {secs_passed}s"
            time_left = max(0, 480 - int(delta.total_seconds()))
            remaining = f"{time_left // 60}m {time_left % 60}s"

        if participants:
            lines = []
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            for uid, slot in sorted(participants.items(), key=lambda x: x[1]):
                medal = medals.get(slot, f"**#{slot}**")
                member = ctx.guild.get_member(uid)
                name = member.display_name if member else f"User#{uid}"
                lines.append(f"{medal} **{name}**")
            registrant_list = "\n".join(lines)
        else:
            registrant_list = "*No one yet…*"

        em = make_embed(
            title=f"🟢  {current_event_name} Registration is LIVE!",
            description=(
                f"```\n[{progress}] {slots_taken}/10 slots claimed\n```\n"
                f"React with {REGISTER_EMOJI} on the session message to register!"
            ),
            color=EMBED_COLOR_SUCCESS,
            fields=[
                ("🎰 Slots Left", f"**{slots_left}**", True),
                ("⏱️ Elapsed", elapsed or "—", True),
                ("⏳ Remaining", remaining or "—", True),
                ("📝 Registered", registrant_list, False),
            ],
        )
    else:
        now = datetime.now(UK_TZ)
        time_str = now.strftime("**%H:%M**")
        
        em = make_embed(
            title="🔴  No Active Poll",
            description=(
                f"Current UK Time: {time_str}\n\n"
                "Registration polls trigger automatically based on the schedule.\n"
                "Use `!events` to see the full timetable! ⏳"
            ),
            color=EMBED_COLOR_WARN,
        )

    await ctx.reply(embed=em, mention_author=False)

# ---------- !registrations ----------
@bot.command(name="registrations", aliases=["list", "regs"])
async def registrations_cmd(ctx):
    """Show the currently registered participants."""
    if not active_session:
        em = make_embed(
            title="🔴  No Active Session",
            description="There's no session running right now, so no one is registered.",
            color=EMBED_COLOR_WARN,
        )
        await ctx.reply(embed=em, mention_author=False)
        return

    if not participants:
        registrant_list = "*No one has registered yet!*"
    else:
        lines = []
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for uid, slot in sorted(participants.items(), key=lambda x: x[1]):
            medal = medals.get(slot, f"**#{slot}**")
            member = ctx.guild.get_member(uid)
            name = member.display_name if member else f"User#{uid}"
            lines.append(f"{medal} **{name}**")
        registrant_list = "\n".join(lines)

    slots_taken = len(participants)
    slots_left = 10 - slots_taken

    em = make_embed(
        title="📝  Current Registrations",
        description=f"**{slots_taken}/10** slots claimed.\n\n{registrant_list}",
        color=EMBED_COLOR,
        fields=[
            ("🎰 Slots Left", f"**{slots_left}**", True),
        ]
    )
    await ctx.reply(embed=em, mention_author=False)

# ---------- !start ----------
@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start_cmd(ctx):
    """Manually start a registration session (Admin only)."""
    global active_session

    if active_session:
        await ctx.reply("⚠️ A session is already active!", delete_after=10)
        return

    # Use the unified open_poll logic
    asyncio.create_task(open_poll(["Manual Session"]))
    await ctx.reply(f"✅ Session started in <#{channel_id}>!", delete_after=10)


# ---------- !events ----------
@bot.command(name="events", aliases=["schedule"])
async def events_cmd(ctx):
    """Show the full event schedule (UK Time)."""
    lines = []
    for time_str, name, days in EVENT_LIST:
        day_info = ""
        if days:
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_info = f" ({', '.join([day_names[d] for d in days])})"
        lines.append(f"**{time_str}** — {name}{day_info}")
    
    schedule_text = "\n".join(lines)
    
    gun_loss_text = ", ".join(GUN_LOSS_EVENTS)
    no_loss_text = ", ".join(NO_GUN_LOSS_EVENTS)
    
    em = make_embed(
        title="📅  Grand RP Event Schedule (UK Time)",
        description=(
            f"Registration polls trigger automatically at these times!\n\n"
            f"{schedule_text}"
        ),
        color=EMBED_COLOR,
        fields=[
            ("⚠️ Gun & Ammo Loss", f"You lose gear in: **{gun_loss_text}**.\n*(Note: Gear is safe if you have Prime Platinum)*", False),
            ("✅ Safe Events", f"You don't lose gear in: **{no_loss_text}**.", False),
        ]
    )
    await ctx.reply(embed=em, mention_author=False)


# ---------- !clean ----------
@bot.command(name="clean", aliases=["purge", "clear"])
@commands.has_permissions(manage_messages=True)
async def clean_cmd(ctx, amount: int = 100):
    """Purge messages from the channel (Admin only)."""
    # Limit amount to avoid issues
    amount = min(amount, 500)
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1) # +1 to include the command itself
        confirm_em = make_embed(
            title="🧹  Channel Cleaned!",
            description=f"Successfully purged **{len(deleted)-1}** messages.",
            color=EMBED_COLOR_SUCCESS,
        )
        temp_msg = await ctx.send(embed=confirm_em)
        await asyncio.sleep(5)
        await temp_msg.delete()
    except discord.Forbidden:
        await ctx.reply("❌ I don't have permission to manage messages!", delete_after=5)
    except Exception as e:
        await ctx.reply(f"⚠️ An error occurred: {e}", delete_after=5)


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
                ("!status", "Check if a session is running & see registrations.", False),
                ("!events", "Show the full event schedule. 📅", False),
                ("!registrations", "List current participants.", False),
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
    print(f"🔁 UK Event scheduler loop started")
    event_scheduler.start()


# =========================
# 🔑 START BOT (token from .env)
# =========================
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("❌ DISCORD_TOKEN not found in .env file!")
bot.run(token)
