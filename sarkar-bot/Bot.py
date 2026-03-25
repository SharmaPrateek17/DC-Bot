import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound
import asyncio
import random
import os
import json
from datetime import datetime, timedelta
from collections import Counter
import aiohttp
import threading

import pytz
from dotenv import load_dotenv

load_dotenv()

# =========================
# 🔹 CHANNEL & ROLE IDs
# =========================
# Paste your Discord channel IDs below for each section.

CHANNEL_IDS = {
    "INFORMAL":      1473346234763706549,   # <-- Paste your Informal Section channel ID
    "STATE_CONTROL": 1475815532631560359,   # <-- Paste your State Control Section channel ID
    "BIZ_WAR":       1475816139358732371,   # <-- Paste your Biz War Section channel ID
    "RP_TICKET":     1475816007900725298,   # <-- Paste your RP Ticket Section channel ID
    "OTHER_EVENTS":  1476228818917392424,   # <-- Paste your Other Events Section channel ID
}

allowed_role_id = 1467869329256091648  # <-- Replace with your role ID
FAMILY_ROLE_ID  = 1467869393282138405  # Family role to mention during events
SPECIAL_EVENT_CHANNEL_ID = 1480059758831603804  # Channel for Special Events reminders
PAGER_CHANNEL_ID = 1476312468140724267        # Channel to send the pager messages
BIZ_WAR_MANAGER_ROLE_ID = 1482325911788327022  # Role allowed to manage Biz War lists

# --- Announcement System Settings ---
ANNOUNCEMENT_LOG_CHANNEL_ID = 0  # Placeholder, user can update this
BAN_LOG_CHANNEL_ID = 1483808211923374120  # Channel for ban audit logs
BAN_REPORT_CHANNEL_ID = 1483808211923374120  # Channel for ban report embeds

# =========================
# 🎨 THEME
# =========================

EMBED_COLOR         = 0x7C3AED   # Vibrant purple
EMBED_COLOR_SUCCESS = 0x10B981   # Emerald green
EMBED_COLOR_WARN    = 0xF59E0B   # Amber
EMBED_COLOR_CLOSE   = 0xEF4444   # Red
FOOTER_TEXT = "Event Automation Manager ✦"
QUOTES_API_KEY = "DIoJIFBD6Fi92uinGVyfg2yZzmVPKSh0yNPxa9ca"

# Registration emoji — users react with this to register
REGISTER_EMOJI = "🎟️"

# =========================
# 🎨 MUSIC EMBED COLORS (kept for general use)
# =========================

MUSIC_EMBED_COLOR2 = 0x818CF8  # Indigo for info/general

# =========================
# 🎲 FUN DATA
# =========================

SLOT_EMOJIS = [
    "🔥", "⭐", "🎯", "💎", "🚀", "🏆", "💫", "✨", "🎉", "👑",
    "⚡", "🌟", "🎪", "🎭", "🎬", "🎰", "🎲", "🃏", "🏅", "🎖️",
    "💥", "🌈", "🎸", "🎺", "🎻",
]

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

# =========================
# 📟 PAGER MESSAGES
# =========================

PAGER_MESSAGES = {
    "Serious": [
        "All family members are requested to come to the city and prepare for upcoming events. Active participation will be rewarded with bonus payments.",
        "⚠️ Family Notice: Events are starting soon. All members should report to the city and be ready for participation."
    ],
    "Motivational": [
        "🔥 Fam Call: Events are about to begin! Come to the city, show your skills, and earn extra bonuses.",
        "💪 Family Power: Strong families move together. Join the events in the city and help us dominate."
    ],
    "Funny": [
        "😂 Fam Pager: If you're sleeping wake up. If you're eating finish fast. Events are starting and bonuses are waiting.",
        "🤣 Friendly Reminder: The city is calling. Your bonus might get stolen by someone else if you stay offline."
    ],
    "Hype": [
        "⚡ Fam Alert: Events are starting soon. Everyone report to the city and prepare to dominate.",
        "🔥 Battle Time: No spectators today. Only fighters. Join the event and earn your bonus."
    ],
    "Threat": [
        "🚨 Family Warning: Events are starting. Those who join will get bonuses... those who don't will be remembered.",
        "👀 Leader Notice: The family is gathering in the city. Missing this event might cost you your bonus."
    ],
    "Chill": [
        "📢 Fam Reminder: Events are happening in the city right now. Come join and earn some extra bonuses.",
        "🎯 Easy Bonus Time: Join the event session in the city and have some fun with the family."
    ]
}
# =========================
# 📅 EVENT SCHEDULE (UK Time)
# =========================
# Format: (HH:MM, Event Name, Channel Key, Max Participants, Days, Description)
# Days: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
# If days is None → triggers every day.

EVENT_LIST = [
    # ── INFORMAL SECTION (every hour at :30, all day) ──
] + [(f"{h:02d}:30", "🎉 Informal 🎉", "INFORMAL", 10, None, None) for h in range(24)] + [
    # ── BIZ WAR SECTION ──
    ("01:05", "💼 Business War 💼",               "BIZ_WAR",       25, None, None),
    ("19:05", "💼 Business War 💼",               "BIZ_WAR",       25, None, None),
    # ── STATE CONTROL SECTION (16:00–23:00 window) ──
    ("16:00", "🏛️ State Control 🏛️",              "STATE_CONTROL",  10, None, "Active between 16:00–23:00 UK Time."),
    # ── RP TICKET SECTION ──
    ("10:30", "🎫 Factory of RP Tickets 🎫",      "RP_TICKET",      25, None, None),
    ("16:30", "🎫 Factory of RP Tickets 🎫",      "RP_TICKET",      25, None, None),
    ("22:30", "🎫 Factory of RP Tickets 🎫",      "RP_TICKET",      25, None, None),
    # ── OTHER EVENTS SECTION ──
    ("00:00", "🌿 Weed Farm 🌿",                  "OTHER_EVENTS",   25, None, None),
    ("01:10", "⚓ Harbor ⚓",                     "OTHER_EVENTS",   25, None, None),
    ("02:00", "🌿 Weed Farm 🌿",                  "OTHER_EVENTS",   25, None, None),
    ("02:20", "🏨 Hotel Takeover 🏨",             "OTHER_EVENTS",   25, None, None),
    ("03:20", "🔫 Weapons Factory 🔫",            "OTHER_EVENTS",   25, None, None),
    ("04:10", "⚓ Harbor ⚓",                     "OTHER_EVENTS",   25, None, None),
    ("06:00", "🌿 Weed Farm 🌿",                  "OTHER_EVENTS",   25, None, None),
    ("07:10", "⚓ Harbor ⚓",                     "OTHER_EVENTS",   25, None, None),
    ("07:20", "🔫 Weapons Factory 🔫",            "OTHER_EVENTS",   25, None, None),
    ("08:00", "🌿 Weed Farm 🌿",                  "OTHER_EVENTS",   25, None, None),
    ("10:00", "🌿 Weed Farm 🌿",                  "OTHER_EVENTS",   25, None, None),
    ("10:10", "⚓ Harbor ⚓",                     "OTHER_EVENTS",   25, None, None),
    ("10:20", "🔫 Weapons Factory 🔫",            "OTHER_EVENTS",   25, None, None),
    ("12:00", "🌿 Weed Farm 🌿",                  "OTHER_EVENTS",   25, None, None),
    ("13:10", "⚓ Harbor ⚓",                     "OTHER_EVENTS",   25, None, None),
    ("14:00", "🌿 Weed Farm 🌿",                  "OTHER_EVENTS",   25, None, None),
    ("14:20", "🔥 Foundry 🔥",                    "OTHER_EVENTS",   25, None, None),
    ("16:00", "🌿 Weed Farm 🌿",                  "OTHER_EVENTS",   25, None, None),
    ("16:10", "⚓ Harbor ⚓",                     "OTHER_EVENTS",   25, None, None),
    ("22:20", "🔫 Weapons Factory 🔫",            "OTHER_EVENTS",   25, None, None),
]

# ── SPECIAL EVENTS SECTION ──
SPECIAL_EVENT_LIST = [
    ("17:15", "🏬 Mall 🏬",                       None,    5, None, "17:15 Registration · 17:20 Defense enters · 17:25 Attack enters"),
    ("17:30", "🏦 Bank Robbery 🏦",               None,   25, [0, 2, 5], "Registration at 17:30 for 21:30 event."),
    ("20:20", "🔓 Prison Protection 🔓",           None,   25, [4],      None),
    ("10:00", "🧪 Drug Lab 🧪",                   None,   25, None, "Active between 10:00–23:00 UK Time."),
]
# =========================
# ⚠️ GUN LOSS RULES
# =========================

GUN_LOSS_EVENTS    = ["Business War", "Hotel Takeover", "Rating Battle"]
NO_GUN_LOSS_EVENTS = ["Harbor", "Foundry", "Mall", "Vineyard", "Weapons Factory"]

# =========================
# ⚙️ BOT SETUP
# =========================

UK_TZ = pytz.timezone("Europe/London")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Per-channel session tracking: {channel_id: session_dict}
# session_dict keys: event_name, max_participants, confirmed (list),
#   waiting_list (list), start_time, message_id, channel_id, description
active_sessions = {}

all_time_leaderboard = Counter()  # {user_id: count}
bot_start_time = None  # Set in on_ready for uptime tracking


# =========================
# 📦 HELPERS
# =========================

def get_event_gif(event_name):
    """
    Load GIF configuration and return a matching URL for the event.
    GIFs can be edited in the config/eventGifs.json file.
    """
    try:
        with open("config/eventGifs.json", "r", encoding="utf-8") as f:
            gifs = json.load(f)
            for key, url in gifs.items():
                if key.lower() in event_name.lower():
                    return url
    except Exception as e:
        print(f"⚠️ Could not load eventGifs.json: {e}")
    return None

def get_bot_gif(key_name):
    """
    Load a general bot GIF from config/botGifs.json.
    Keys like 'HELP_GIF', 'ANNOUNCEMENT_GIF', etc.
    """
    try:
        with open("config/botGifs.json", "r", encoding="utf-8") as f:
            gifs = json.load(f)
            return gifs.get(key_name)
    except Exception as e:
        print(f"⚠️ Could not load botGifs.json: {e}")
    return None

# ============================================================
# TEMPLATE HELPER FUNCTIONS
# ============================================================
def load_announcement_templates():
    try:
        with open("config/annTemplates.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_announcement_template(name, title_text, body_text):
    templates = load_announcement_templates()
    templates[name] = {"title": title_text, "body": body_text}
    
    os.makedirs("config", exist_ok=True)
    with open("config/annTemplates.json", "w") as f:
        json.dump(templates, f, indent=4)

# ============================================================
# EVENT HELPER FUNCTIONS
# ============================================================

def get_gun_info(event_name):
    """Return gun-loss warning string, or empty string if not applicable."""
    for ev in GUN_LOSS_EVENTS:
        if ev.lower() in event_name.lower():
            return "❌ **LOSE GUN/AMMO ON DEATH** *(safe with Prime Platinum)*"
    for ev in NO_GUN_LOSS_EVENTS:
        if ev.lower() in event_name.lower():
            return "✅ **DO NOT lose gun/ammo on death**"
    return ""


def make_embed(title, description, color=EMBED_COLOR, fields=None):
    """Build a styled embed."""
    em = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(UK_TZ),
    )
    em.set_footer(text=FOOTER_TEXT)
    if fields:
        for name, value, inline in fields:
            em.add_field(name=name, value=value, inline=inline)
    return em


def _member_name(channel, uid):
    """Resolve a display name from a channel + user ID."""
    if channel and channel.guild:
        member = channel.guild.get_member(uid)
        if member:
            return member.display_name
    return f"User#{uid}"
def _is_biz_war_channel(channel_id):
    """Check if a channel ID is the Biz War channel."""
    return channel_id == CHANNEL_IDS.get("BIZ_WAR", 0)


def build_session_embed(session, is_open=True):
    """Build the live registration embed for a session."""
    event_name = session["event_name"]
    max_p      = session["max_participants"]
    confirmed  = session["confirmed"]
    waiting    = session["waiting_list"]
    desc       = session.get("description") or ""
    ch         = bot.get_channel(session["channel_id"])
    is_biz_war = _is_biz_war_channel(session["channel_id"])

    # ── Confirmed list ──
    if confirmed:
        lines = []
        for i, uid in enumerate(confirmed, 1):
            if is_biz_war:
                member = ch.guild.get_member(uid) if ch and ch.guild else None
                mention = member.mention if member else f"User#{uid}"
                lines.append(f"**{i}.** {mention}")
            else:
                emoji = SLOT_EMOJIS[i - 1] if i <= len(SLOT_EMOJIS) else "🎉"
                lines.append(f"{emoji} **#{i}** — **{_member_name(ch, uid)}**")
        confirmed_text = "\n".join(lines)
    else:
        confirmed_text = "*No one yet… be the first!*"

    # ── Waiting list ──
    waiting_text = ""
    if waiting:
        if is_biz_war:
            wl = []
            for i, uid in enumerate(waiting, 1):
                member = ch.guild.get_member(uid) if ch and ch.guild else None
                mention = member.mention if member else f"User#{uid}"
                wl.append(f"**{i}.** {mention}")
            waiting_text = "\n".join(wl)
        else:
            wl = [f"**#{i}** — {_member_name(ch, uid)}" for i, uid in enumerate(waiting, 1)]
            waiting_text = "\n".join(wl)

    # ── Build embed based on event type ──
    gun_info = get_gun_info(event_name)
    now_str  = datetime.now(UK_TZ).strftime("%H:%M")
    status   = "🟢 OPEN" if is_open else "🔴 CLOSED"

    if is_biz_war:
        # ── Biz War specific layout ──
        fields = []
        if desc:
            fields.append(("📖 Details", desc, False))
        if gun_info:
            fields.append(("⚔️ Gear Rule", gun_info, False))

        fields.append((f"👥 Current Members ({len(confirmed)}/{max_p})", confirmed_text, False))
        if waiting:
            fields.append(("⏳ Waiting List", waiting_text, False))
        fields.append(("📍 Status", status, True))

        em = make_embed(
            title="💼  Biz War Event",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 **UK Time:** {now_str}\n"
                f"🎯 **Event:** {event_name}\n"
                f"👥 **Max Members:** {max_p}\n\n"
                f"React with {REGISTER_EMOJI} to join.\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR if is_open else EMBED_COLOR_CLOSE,
            fields=fields,
        )
    else:
        # ── Standard layout for other events ──
        fields = []
        if desc:
            fields.append(("📖 Details", desc, False))
        if gun_info:
            fields.append(("⚔️ Gear Rule", gun_info, False))

        fields += [
            ("👥 Confirmed", f"**{len(confirmed)} / {max_p}**", True),
            ("🕒 Waiting List", f"**{len(waiting)}**", True),
            ("📍 Status", status, True),
            ("📝 Confirmed Members", confirmed_text, False),
        ]
        if waiting:
            fields.append(("⏳ Waiting List", waiting_text, False))

        em = make_embed(
            title="📢  EVENT REMINDER",
            description=(
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 **UK Time:** {now_str}\n"
                f"🎯 **Event:** {event_name}\n"
                f"👥 **Max Members:** {max_p}\n\n"
                f"React with {REGISTER_EMOJI} to join.\n"
                f"━━━━━━━━━━━━━━━━━━"
            ),
            color=EMBED_COLOR if is_open else EMBED_COLOR_CLOSE,
            fields=fields,
        )
    
    # ── EVENT GIF SYSTEM ──
    # Display the GIF inside the embed
    gif_url = get_event_gif(event_name)
    if gif_url:
        em.set_image(url=gif_url)
        
    return em
# =========================
# ⏰ OPEN / CLOSE SESSION
# =========================

async def open_session(target_channel_id, event_name, max_participants, description=None, custom_timer_seconds=480, custom_gif=None):
    """Open a registration session in a specific channel."""
    channel = bot.get_channel(target_channel_id)
    if channel is None:
        print(f"⚠️ Channel {target_channel_id} not found!")
        return

    if target_channel_id in active_sessions:
        print(f"⚠️ Session already active in #{channel.name}, skipping {event_name}")
        return

    session = {
        "event_name":       event_name,
        "max_participants":  max_participants,
        "confirmed":         [],
        "waiting_list":      [],
        "cancelled_users":   [],
        "pending_tickets":   set(),
        "start_time":        datetime.now(UK_TZ),
        "message_id":        None,
        "channel_id":        target_channel_id,
        "description":       description,
    }

    # Channel permissions are no longer modified automatically

    em = build_session_embed(session)

    # ── Attach management buttons for all sessions ──
    mgmt_view = SessionManagementView(target_channel_id)
    msg = await channel.send(content=f"<@&{FAMILY_ROLE_ID}>", embed=em, view=mgmt_view)
    
    # ── EVENT GIF SYSTEM ──
    # Display the GIF inside the embed (custom_gif overrides get_event_gif)
    gif_url = custom_gif if custom_gif else get_event_gif(event_name)
    if gif_url and gif_url != "none":
        em.set_image(url=gif_url)
        # Re-edit the message with the image
        await msg.edit(embed=em, view=mgmt_view)
        
    session["message_id"] = msg.id
    active_sessions[target_channel_id] = session

    await msg.add_reaction(REGISTER_EMOJI)
    print(f"📢 Session opened: {event_name} in #{channel.name} (UK: {session['start_time'].strftime('%H:%M')})")

    # Auto-close after custom_timer_seconds (default 8 minutes)
    await asyncio.sleep(custom_timer_seconds)
    if target_channel_id in active_sessions and active_sessions[target_channel_id]["message_id"] == msg.id:
        await close_session(target_channel_id)


async def close_session(target_channel_id):
    """Close a registration session and post summary."""
    if target_channel_id not in active_sessions:
        return

    session = active_sessions.pop(target_channel_id)
    channel = bot.get_channel(target_channel_id)
    if channel is None:
        return

    # Channel permissions are no longer modified automatically

    confirmed  = session["confirmed"]
    event_name = session["event_name"]
    medals     = {1: "🥇", 2: "🥈", 3: "🥉"}

    # Build participant list
    if confirmed:
        lines = [f"{medals.get(i, f'#{i}')} **{_member_name(channel, uid)}**"
                 for i, uid in enumerate(confirmed, 1)]
        user_list = "\n".join(lines)
    else:
        user_list = "*No one showed up… maybe next time!* 😢"

    elapsed = ""
    if session["start_time"]:
        delta = datetime.now(UK_TZ) - session["start_time"]
        mins  = int(delta.total_seconds() // 60)
        secs  = int(delta.total_seconds() % 60)
        elapsed = f"{mins}m {secs}s"

    em = make_embed(
        title="🔒  Registration CLOSED",
        description=(
            f"Registration for **{event_name}** is now **closed**.\n\n"
            f"**{len(confirmed)}/{session['max_participants']}** slots confirmed."
        ),
        color=EMBED_COLOR_CLOSE,
        fields=[
            ("👥 Participants", user_list, False),
            ("⏱️ Duration", elapsed or "—", True),
            ("📊 Total Confirmed", f"{len(confirmed)} / {session['max_participants']}", True),
        ],
    )
    
    # ── Add Registration Closed GIF ──
    reg_closed_gif = get_bot_gif("REGISTRATION_CLOSED_GIF")
    if reg_closed_gif:
        em.set_image(url=reg_closed_gif)
        
    await channel.send(embed=em)

    # Post clean final summary
    if confirmed:
        summary_lines = [f"{medals.get(i, f'#{i}')} {_member_name(channel, uid)}"
                         for i, uid in enumerate(confirmed, 1)]
        summary_text = "\n".join(summary_lines)
    else:
        summary_text = "No participants."

    clean_em = make_embed(
        title=f"📋  {event_name} — Summary",
        description=(
            f"**{len(confirmed)}** member(s) confirmed.\n"
            f"Duration: **{elapsed or '—'}**\n\n"
            f"{summary_text}\n\n"
            f"*Next event will trigger automatically.* ⏳"
        ),
        color=EMBED_COLOR,
    )
    
    # ── Add Event Summary GIF ──
    summary_gif = get_bot_gif("EVENT_SUMMARY_GIF")
    if summary_gif:
        clean_em.set_image(url=summary_gif)
        
    await channel.send(embed=clean_em)
    print(f"🔒 Session closed: {event_name} in #{channel.name}")
# =========================
# ⏰ EVENT SCHEDULER
# =========================

@tasks.loop(minutes=1)
async def event_scheduler():
    now              = datetime.now(UK_TZ)
    current_time_str = now.strftime("%H:%M")
    current_day      = now.weekday()

    # ── Biz War Early Reminder (10 minutes before event) ──
    biz_war_ch_id = CHANNEL_IDS.get("BIZ_WAR", 0)
    if biz_war_ch_id != 0:
        for time_str, name, ch_key, max_p, days, desc in EVENT_LIST:
            if ch_key != "BIZ_WAR":
                continue
            if days is not None and current_day not in days:
                continue

            # Calculate 10 minutes before event time
            evt_h, evt_m = map(int, time_str.split(":"))
            reminder_time = datetime(now.year, now.month, now.day, evt_h, evt_m, tzinfo=UK_TZ) - timedelta(minutes=10)
            reminder_time_str = reminder_time.strftime("%H:%M")

            if current_time_str == reminder_time_str:
                channel = bot.get_channel(biz_war_ch_id)
                if channel is None:
                    continue

                # Build member ping list from active session (if one exists)
                member_pings = ""
                if biz_war_ch_id in active_sessions:
                    session = active_sessions[biz_war_ch_id]
                    all_members = session["confirmed"] + session["waiting_list"]
                    if all_members:
                        pings = [f"<@{uid}>" for uid in all_members]
                        member_pings = "\n".join(pings)

                reminder_em = make_embed(
                    title="⏰  Biz War Starting Soon!",
                    description=(
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"💼 **BIZ WAR starting in 10 minutes**\n"
                        f"🕒 **Event Time:** {time_str} UK\n\n"
                        f"Get ready and be prepared!\n"
                        f"━━━━━━━━━━━━━━━━━━"
                    ),
                    color=EMBED_COLOR_WARN,
                )

                if member_pings:
                    reminder_em.add_field(name="📋 Registered Members", value=member_pings, inline=False)

                await channel.send(content=f"<@&{FAMILY_ROLE_ID}>", embed=reminder_em)
                print(f"⏰ Biz War early reminder sent for {name} at {time_str} (reminder at {reminder_time_str})")

    # ── RP Factory Multi-Reminders ──
    rp_factory_times = ["10:30", "16:30", "22:30"]
    rp_factory_ch_id = 1486052630655668294
    rp_factory_ch = bot.get_channel(rp_factory_ch_id)
    if rp_factory_ch:
        rp_intervals = {
            60: "1 hour",
            45: "45 minutes",
            30: "30 minutes",
            15: "15 minutes",
            5: "5 minutes"
        }
        rp_messages = [
            "Guys Pull Up for RP Factory 🎟️",
            "Wake up! RP Factory is coming 🔥",
            "Easy profit waiting 💰",
            "Final call — don’t miss out ⚠️",
            "Time to grind, RP Factory let's go! 🚀"
        ]
        
        for t_str in rp_factory_times:
            evt_h, evt_m = map(int, t_str.split(":"))
            for mins, label in rp_intervals.items():
                rem_time = datetime(now.year, now.month, now.day, evt_h, evt_m, tzinfo=UK_TZ) - timedelta(minutes=mins)
                if current_time_str == rem_time.strftime("%H:%M"):
                    gif_url = get_event_gif("RP Ticket") or get_event_gif("RP Factory")
                    msg_text = random.choice(rp_messages)
                    
                    rem_em = make_embed(
                        title="🎫  RP Factory Reminder",
                        description=(
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"📣 **{msg_text}**\n"
                            f"⏳ RP Factory starts in **{label}**!\n"
                            f"🕒 **Event Time:** {t_str} UK\n"
                            f"━━━━━━━━━━━━━━━━━━"
                        ),
                        color=EMBED_COLOR_WARN
                    )
                    
                    if gif_url:
                        rem_em.set_image(url=gif_url)
                        
                    async def send_rp_reminders(channel, embed):
                        content = f"<@&{FAMILY_ROLE_ID}>"
                        for _ in range(3):
                            await channel.send(content=content, embed=embed)
                            await asyncio.sleep(2.0)
                            
                    asyncio.create_task(send_rp_reminders(rp_factory_ch, rem_em))
                    print(f"⏰ RP Factory {label} reminder sent for {t_str}")

    # ── Special Event Early Reminders (10 minutes before — Drug Lab, Bank Robbery, Mall) ──
    SIMPLE_REMINDER_EVENTS = {"drug lab", "bank robbery", "mall"}
    SIMPLE_REMINDER_MESSAGES = {
        "drug lab": "Drug Lab starting in 10 minutes",
        "bank robbery": "Bank Robbery starting in 10 minutes",
        "mall": "Mall Event starting in 10 minutes",
    }
    special_ch = bot.get_channel(SPECIAL_EVENT_CHANNEL_ID)
    if special_ch:
        for time_str, name, ch_key, max_p, days, desc in SPECIAL_EVENT_LIST:
            if days is not None and current_day not in days:
                continue

            event_key = None
            for key in SIMPLE_REMINDER_EVENTS:
                if key in name.lower():
                    event_key = key
                    break
            if event_key is None:
                continue

            # Calculate 10 minutes before event time
            evt_h, evt_m = map(int, time_str.split(":"))
            reminder_time = datetime(now.year, now.month, now.day, evt_h, evt_m, tzinfo=UK_TZ) - timedelta(minutes=10)
            reminder_time_str = reminder_time.strftime("%H:%M")

            if current_time_str == reminder_time_str:
                reminder_text = SIMPLE_REMINDER_MESSAGES[event_key]
                gif_url = get_event_gif(event_key)
                reminder_em = make_embed(
                    title="⏰  Event Reminder",
                    description=(
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"📢 **{reminder_text}**\n"
                        f"🕒 **Event Time:** {time_str} UK\n"
                        f"━━━━━━━━━━━━━━━━━━"
                    ),
                    color=EMBED_COLOR_WARN,
                )
                if gif_url:
                    reminder_em.set_image(url=gif_url)
                content = f"<@&{FAMILY_ROLE_ID}>"
                await special_ch.send(content=content, embed=reminder_em)
                print(f"⏰ Simple reminder sent: {reminder_text} (event at {time_str})")

        # ── Mall Event Extra Reminders ──
        if current_time_str == "17:10":
            gif_url = get_event_gif("Mall")
            em = make_embed(
                title="🏬  Mall Event Reminder",
                description=(
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📢 **Get ready for Mall Event**\n"
                    f"🕒 **Starts Soon**\n"
                    f"━━━━━━━━━━━━━━━━━━"
                ),
                color=EMBED_COLOR_WARN
            )
            if gif_url:
                em.set_image(url=gif_url)
            content = f"<@&{FAMILY_ROLE_ID}>"
            await special_ch.send(content=content, embed=em)
            print("⏰ Mall Event 17:10 reminder sent")

        if current_time_str == "17:16":
            gif_url = get_event_gif("Mall")
            em = make_embed(
                title="🏬  Mall Registration",
                description=(
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📢 **Only 5 slots available**\n"
                    f"⚡ **Join fast**\n"
                    f"━━━━━━━━━━━━━━━━━━"
                ),
                color=EMBED_COLOR_WARN
            )
            if gif_url:
                em.set_image(url=gif_url)
            content = f"<@&{FAMILY_ROLE_ID}>"
            await special_ch.send(content=content, embed=em)
            print("⏰ Mall Event 17:16 registration reminder sent")

        # ── Bank Robbery Extra Reminders ──
        br_reminders = {
            "17:25": ("🏦  Bank Robbery Registration", "📢 **Registration opening in 5 minutes**\n⚡ **Be ready to join!**"),
            "21:00": ("🏦  Bank Robbery Event", "📢 **Event participation reminder**\n🔥 **Get ready for the Bank Robbery!**"),
            "21:15": ("🏦  Bank Robbery Final Call", "📢 **Final call — don’t miss out ⚠️**\n⚡ **Event starting very soon!**")
        }
        
        if current_time_str in br_reminders:
            title, desc_text = br_reminders[current_time_str]
            gif_url = get_event_gif("Bank Robbery")
            em = make_embed(
                title=title,
                description=(
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{desc_text}\n"
                    f"━━━━━━━━━━━━━━━━━━"
                ),
                color=EMBED_COLOR_WARN
            )
            if gif_url:
                em.set_image(url=gif_url)
            content = f"<@&{FAMILY_ROLE_ID}>"
            await special_ch.send(content=content, embed=em)
            print(f"⏰ Bank Robbery {current_time_str} reminder sent")

    events_by_channel = {}
    
    # Process standard events
    for time_str, name, ch_key, max_p, days, desc in EVENT_LIST:
        if time_str != current_time_str:
            continue
        if days is not None and current_day not in days:
            continue

        target_ch_id = CHANNEL_IDS.get(ch_key, 0)
        if target_ch_id == 0:
            print(f"⚠️ Channel key '{ch_key}' not configured, skipping {name}")
            continue

        events_by_channel.setdefault(target_ch_id, []).append((name, max_p, desc))

    # Process special events — only events that are NOT simple-reminder-only
    for time_str, name, ch_key, max_p, days, desc in SPECIAL_EVENT_LIST:
        if time_str != current_time_str:
            continue
        if days is not None and current_day not in days:
            continue

        # Skip Drug Lab, Bank Robbery, Mall — they only get simple reminders now
        is_simple_reminder = any(key in name.lower() for key in SIMPLE_REMINDER_EVENTS)
        if is_simple_reminder:
            print(f"📢 Skipping session for {name} — uses simple reminder only")
            continue
            
        target_ch_id = SPECIAL_EVENT_CHANNEL_ID
        events_by_channel.setdefault(target_ch_id, []).append((name, max_p, desc))

    # Open one session per channel (combine events if multiple match)
    for ch_id, events in events_by_channel.items():
        if ch_id in active_sessions:
            names = ", ".join(e[0] for e in events)
            print(f"⚠️ Skipping {names} — session already active in channel {ch_id}")
            continue

        combined_name = " & ".join(e[0] for e in events)
        combined_max  = min(e[1] for e in events)
        descriptions  = [e[2] for e in events if e[2]]
        combined_desc = " | ".join(descriptions) if descriptions else None

        asyncio.create_task(open_session(ch_id, combined_name, combined_max, combined_desc))


# =========================
# 🧹 24-HOUR AUTO-CLEAN
# =========================

@tasks.loop(hours=24)
async def auto_clean_channels():
    """Purge all event channels every 24 hours."""
    print("🧹 Running 24-hour auto-clean for all event channels...")
    for ch_key, ch_id in CHANNEL_IDS.items():
        if ch_id == 0 or ch_id in active_sessions:
            print(f"   ⏭️ Skipping {ch_key} (active session or not configured)")
            continue
        channel = bot.get_channel(ch_id)
        if channel is None:
            continue
        try:
            deleted = await channel.purge(limit=500)
            if deleted:
                print(f"   🧹 Auto-cleaned {len(deleted)} messages from #{channel.name}")
        except discord.Forbidden:
            print(f"   ⚠️ Missing permissions to purge #{channel.name}")
        except Exception as e:
            print(f"   ⚠️ Auto-clean error in #{channel.name}: {e}")
    print("🧹 24-hour auto-clean complete.")

@auto_clean_channels.before_loop
async def before_auto_clean():
    """Wait for bot to be ready, then wait 24 hours before the first clean."""
    await bot.wait_until_ready()
    print("🧹 Auto-clean scheduled — first clean in 24 hours.")
    await asyncio.sleep(86400)  # Wait 24 hours before first run
# =========================
# 📝 SESSION MANAGEMENT VIEW (Move Buttons)
# =========================

class SessionMemberSelect(discord.ui.Select):
    """Dropdown to select a member to move between lists."""

    def __init__(self, channel_id, direction):
        self.channel_id = channel_id
        self.direction = direction  # "to_waiting" or "to_current"

        session = active_sessions.get(channel_id)
        if not session:
            super().__init__(placeholder="No active session", options=[discord.SelectOption(label="None", value="0")], disabled=True)
            return

        ch = bot.get_channel(channel_id)
        source_list = session["confirmed"] if direction == "to_waiting" else session["waiting_list"]

        if not source_list:
            label = "Current List is empty" if direction == "to_waiting" else "Waiting List is empty"
            super().__init__(placeholder=label, options=[discord.SelectOption(label="None", value="0")], disabled=True)
            return

        options = []
        for uid in source_list[:25]:  # Discord max 25 options
            name = _member_name(ch, uid)
            options.append(discord.SelectOption(label=name, value=str(uid)))

        placeholder = "Select member to move to Waiting" if direction == "to_waiting" else "Select member to move to Current"
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        # Role check
        if not any(role.id == BIZ_WAR_MANAGER_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to manage the event lists.", ephemeral=True)
            return

        session = active_sessions.get(self.channel_id)
        if not session:
            await interaction.response.send_message("❌ No active session found.", ephemeral=True)
            return

        uid = int(self.values[0])
        ch = bot.get_channel(self.channel_id)
        name = _member_name(ch, uid)

        if self.direction == "to_waiting":
            # Move from Current → Waiting
            if uid in session["confirmed"]:
                session["confirmed"].remove(uid)
                if uid not in session["waiting_list"]:
                    session["waiting_list"].append(uid)

                # Auto-promote first person from waiting list to fill the slot
                if session["waiting_list"]:
                    # Find the first person who isn't the one we just moved
                    for candidate_uid in list(session["waiting_list"]):
                        if candidate_uid != uid:
                            session["waiting_list"].remove(candidate_uid)
                            if candidate_uid not in session["confirmed"]:
                                session["confirmed"].append(candidate_uid)
                            break

                await interaction.response.send_message(f"✅ **{name}** moved to the Waiting List.", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ **{name}** is not in the Current List.", ephemeral=True)
                return

        elif self.direction == "to_current":
            # Move from Waiting → Current
            if uid in session["waiting_list"]:
                if len(session["confirmed"]) >= session["max_participants"]:
                    await interaction.response.send_message(f"⚠️ Current List is full ({session['max_participants']}/{session['max_participants']}). Remove someone first.", ephemeral=True)
                    return
                session["waiting_list"].remove(uid)
                if uid not in session["confirmed"]:
                    session["confirmed"].append(uid)
                await interaction.response.send_message(f"✅ **{name}** moved to the Current List.", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ **{name}** is not in the Waiting List.", ephemeral=True)
                return

        # Update the session embed
        if ch:
            try:
                msg = await ch.fetch_message(session["message_id"])
                new_view = SessionManagementView(self.channel_id)
                await msg.edit(embed=build_session_embed(session), view=new_view)
            except Exception as e:
                print(f"⚠️ Could not update session embed: {e}")


class SessionManagementView(discord.ui.View):
    """Persistent view with buttons to manage session member lists."""

    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Move to Waiting List", emoji="⏳", style=discord.ButtonStyle.secondary, row=0)
    async def move_to_waiting_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Role check
        if not any(role.id == BIZ_WAR_MANAGER_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to manage the event lists.", ephemeral=True)
            return

        session = active_sessions.get(self.channel_id)
        if not session:
            await interaction.response.send_message("❌ No active session.", ephemeral=True)
            return

        if not session["confirmed"]:
            await interaction.response.send_message("⚠️ Current List is empty, no one to move.", ephemeral=True)
            return

        # Show member select dropdown
        view = discord.ui.View(timeout=60)
        view.add_item(SessionMemberSelect(self.channel_id, "to_waiting"))
        await interaction.response.send_message("Select a member to move to the **Waiting List**:", view=view, ephemeral=True)

    @discord.ui.button(label="Move to Current List", emoji="✅", style=discord.ButtonStyle.success, row=0)
    async def move_to_current_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Role check
        if not any(role.id == BIZ_WAR_MANAGER_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to manage the event lists.", ephemeral=True)
            return

        session = active_sessions.get(self.channel_id)
        if not session:
            await interaction.response.send_message("❌ No active session.", ephemeral=True)
            return

        if not session["waiting_list"]:
            await interaction.response.send_message("⚠️ Waiting List is empty, no one to move.", ephemeral=True)
            return

        if len(session["confirmed"]) >= session["max_participants"]:
            await interaction.response.send_message(f"⚠️ Current List is full ({session['max_participants']}/{session['max_participants']}). Move someone to waiting first.", ephemeral=True)
            return

        # Show member select dropdown
        view = discord.ui.View(timeout=60)
        view.add_item(SessionMemberSelect(self.channel_id, "to_current"))
        await interaction.response.send_message("Select a member to move to the **Current List**:", view=view, ephemeral=True)


# =========================
# 🎟️ REGISTRATION TICKET VIEW (DM Buttons)
# =========================

class RegistrationTicketView(discord.ui.View):
    """DM-based ticket with Confirm/Cancel buttons for event registration."""

    def __init__(self, channel_id, user_id):
        super().__init__(timeout=120)  # 2 minute timeout
        self.channel_id = channel_id
        self.user_id = user_id
        self.responded = False

    @discord.ui.button(label="Confirm Registration", emoji="✅", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your ticket!", ephemeral=True)
            return

        if self.responded:
            await interaction.response.send_message("⚠️ You already responded to this ticket.", ephemeral=True)
            return

        self.responded = True

        # Check if session is still active
        if self.channel_id not in active_sessions:
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content="❌ This session has already closed.", embed=None, view=self)
            return

        session = active_sessions[self.channel_id]
        uid = self.user_id

        # Remove from pending tickets
        session["pending_tickets"].discard(uid)

        # Double-check they haven't been cancelled while pending
        if uid in session["cancelled_users"]:
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(
                content="❌ You cancelled your registration for this event and cannot register again in this session.",
                embed=None, view=self
            )
            return

        # Already registered
        if uid in session["confirmed"] or uid in session["waiting_list"]:
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content="⚠️ You are already registered!", embed=None, view=self)
            return

        channel = bot.get_channel(self.channel_id)
        member = channel.guild.get_member(uid) if channel else None
        name = member.display_name if member else f"User#{uid}"
        max_p = session["max_participants"]

        if len(session["confirmed"]) < max_p:
            # ✅ Add to confirmed
            session["confirmed"].append(uid)
            all_time_leaderboard[uid] += 1
            slot = len(session["confirmed"])
            emoji = SLOT_EMOJIS[slot - 1] if slot <= len(SLOT_EMOJIS) else "🎉"

            print(f"   {emoji} Confirmed #{slot}: {name}")

            # Disable buttons and confirm in DM
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(
                content=f"✅ **Registration Confirmed!** You are **Slot #{slot}** for **{session['event_name']}**.",
                embed=None, view=self
            )

            # Update session embed in the event channel
            if channel:
                try:
                    msg = await channel.fetch_message(session["message_id"])
                    await msg.edit(embed=build_session_embed(session))
                except Exception as e:
                    print(f"⚠️ Could not update embed: {e}")

                # Quick confirmation in channel (auto-deletes)
                confirm_em = make_embed(
                    title=f"{emoji}  Slot #{slot} Confirmed!",
                    description=f"**{name}** {random.choice(SLOT_MESSAGES)}",
                    color=EMBED_COLOR_SUCCESS,
                    fields=[
                        ("👥 Confirmed", f"**{len(session['confirmed'])} / {max_p}**", True),
                        ("🕒 Waiting", f"**{len(session['waiting_list'])}**", True),
                    ],
                )
                temp = await channel.send(embed=confirm_em)
                await asyncio.sleep(15)
                try:
                    await temp.delete()
                except discord.NotFound:
                    pass
        else:
            # ⏳ Add to waiting list
            session["waiting_list"].append(uid)
            position = len(session["waiting_list"])
            print(f"   ⏳ Waiting #{position}: {name}")

            # Disable buttons and confirm in DM
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(
                content=f"⏳ Registration is full! You're **#{position}** on the waiting list for **{session['event_name']}**. If someone leaves, you'll be promoted automatically.",
                embed=None, view=self
            )

            # Update session embed in the event channel
            if channel:
                try:
                    msg = await channel.fetch_message(session["message_id"])
                    await msg.edit(embed=build_session_embed(session))
                except Exception as e:
                    print(f"⚠️ Could not update embed: {e}")

                # Waiting list notification in channel (auto-deletes)
                wait_em = make_embed(
                    title="⏳  Added to Waiting List",
                    description=(
                        f"**{name}**, registration is full!\n"
                        f"You're **#{position}** on the waiting list.\n"
                        f"If someone leaves, you'll be promoted automatically."
                    ),
                    color=EMBED_COLOR_WARN,
                )
                temp = await channel.send(embed=wait_em)
                await asyncio.sleep(15)
                try:
                    await temp.delete()
                except discord.NotFound:
                    pass

    @discord.ui.button(label="Cancel Registration", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your ticket!", ephemeral=True)
            return

        if self.responded:
            await interaction.response.send_message("⚠️ You already responded to this ticket.", ephemeral=True)
            return

        self.responded = True

        # Check if session is still active
        if self.channel_id not in active_sessions:
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content="❌ This session has already closed.", embed=None, view=self)
            return

        session = active_sessions[self.channel_id]
        uid = self.user_id

        # Remove from pending
        session["pending_tickets"].discard(uid)

        # Add to cancelled list
        if uid not in session["cancelled_users"]:
            session["cancelled_users"].append(uid)

        # Disable buttons and confirm cancellation
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            content=f"❌ Registration cancelled for **{session['event_name']}**. You cannot register again for this session.",
            embed=None, view=self
        )

        # Remove reaction from the session message
        channel = bot.get_channel(self.channel_id)
        if channel:
            try:
                msg = await channel.fetch_message(session["message_id"])
                member = channel.guild.get_member(uid)
                if member:
                    await msg.remove_reaction(REGISTER_EMOJI, member)
            except Exception:
                pass

        print(f"   ❌ Cancelled: User#{uid} for {session['event_name']}")

    async def on_timeout(self):
        """If user doesn't respond in 2 minutes, auto-cancel the ticket."""
        if not self.responded:
            self.responded = True

            # Remove from pending if session still exists
            if self.channel_id in active_sessions:
                session = active_sessions[self.channel_id]
                session["pending_tickets"].discard(self.user_id)

                # Remove reaction
                channel = bot.get_channel(self.channel_id)
                if channel:
                    try:
                        msg = await channel.fetch_message(session["message_id"])
                        member = channel.guild.get_member(self.user_id)
                        if member:
                            await msg.remove_reaction(REGISTER_EMOJI, member)
                    except Exception:
                        pass


# =========================
# 🎯 REACTION-BASED REGISTRATION
# =========================

@bot.event
async def on_raw_reaction_add(payload):
    """Track reactions on session messages — DM user with Confirm/Cancel ticket."""
    if payload.user_id == bot.user.id:
        return

    ch_id = payload.channel_id
    if ch_id not in active_sessions:
        return

    session = active_sessions[ch_id]
    if payload.message_id != session["message_id"]:
        return

    # Wrong emoji → remove it
    if str(payload.emoji) != REGISTER_EMOJI:
        channel = bot.get_channel(ch_id)
        if channel:
            try:
                msg    = await channel.fetch_message(session["message_id"])
                member = payload.member or channel.guild.get_member(payload.user_id)
                if member:
                    await msg.remove_reaction(payload.emoji, member)
            except Exception:
                pass
        return

    uid   = payload.user_id
    channel = bot.get_channel(ch_id)
    member  = payload.member or (channel.guild.get_member(uid) if channel else None)
    name    = member.display_name if member else f"User#{uid}"

    # ── BLOCK: User previously cancelled in this session ──
    if uid in session["cancelled_users"]:
        # Remove their reaction
        if channel:
            try:
                msg = await channel.fetch_message(session["message_id"])
                if member:
                    await msg.remove_reaction(REGISTER_EMOJI, member)
            except Exception:
                pass

        # Send block notice in channel (auto-deletes)
        block_em = make_embed(
            title="🚫  Registration Blocked",
            description=(
                f"**{name}**, you cancelled your registration for this event "
                f"and **cannot register again** in this session."
            ),
            color=EMBED_COLOR_CLOSE,
        )
        if channel:
            temp = await channel.send(embed=block_em)
            await asyncio.sleep(10)
            try:
                await temp.delete()
            except discord.NotFound:
                pass
        return

    # ── BLOCK: Already registered or on waiting list ──
    if uid in session["confirmed"] or uid in session["waiting_list"]:
        return

    # ── BLOCK: Already has a pending ticket ──
    if uid in session["pending_tickets"]:
        return

    # ── Send DM ticket with Confirm/Cancel buttons ──
    session["pending_tickets"].add(uid)

    ticket_view = RegistrationTicketView(ch_id, uid)
    ticket_em = make_embed(
        title="🎟️  Event Registration Ticket",
        description=(
            f"**Event:** {session['event_name']}\n"
            f"**Slots:** {len(session['confirmed'])}/{session['max_participants']}\n"
            f"**Waiting List:** {len(session['waiting_list'])}\n\n"
            f"Click **Confirm** to register or **Cancel** to decline.\n"
            f"⚠️ *If you cancel, you cannot register again for this session.*\n\n"
            f"*This ticket expires in 2 minutes.*"
        ),
        color=EMBED_COLOR,
    )

    try:
        if member:
            await member.send(embed=ticket_em, view=ticket_view)
    except discord.Forbidden:
        # DMs disabled — fall back to direct registration (old behavior)
        session["pending_tickets"].discard(uid)
        max_p = session["max_participants"]

        if len(session["confirmed"]) < max_p:
            session["confirmed"].append(uid)
            all_time_leaderboard[uid] += 1
            slot = len(session["confirmed"])
            emoji_char = SLOT_EMOJIS[slot - 1] if slot <= len(SLOT_EMOJIS) else "🎉"
            print(f"   {emoji_char} Confirmed #{slot}: {name} (DM fallback)")

            if channel:
                try:
                    msg = await channel.fetch_message(session["message_id"])
                    await msg.edit(embed=build_session_embed(session))
                except Exception as e:
                    print(f"⚠️ Could not update embed: {e}")

                confirm_em = make_embed(
                    title=f"{emoji_char}  Slot #{slot} Confirmed!",
                    description=f"**{name}** {random.choice(SLOT_MESSAGES)}",
                    color=EMBED_COLOR_SUCCESS,
                    fields=[
                        ("👥 Confirmed", f"**{len(session['confirmed'])} / {max_p}**", True),
                        ("🕒 Waiting", f"**{len(session['waiting_list'])}**", True),
                    ],
                )
                temp = await channel.send(embed=confirm_em)
                await asyncio.sleep(15)
                try:
                    await temp.delete()
                except discord.NotFound:
                    pass
        else:
            session["waiting_list"].append(uid)
            position = len(session["waiting_list"])
            print(f"   ⏳ Waiting #{position}: {name} (DM fallback)")

            if channel:
                try:
                    msg = await channel.fetch_message(session["message_id"])
                    await msg.edit(embed=build_session_embed(session))
                except Exception as e:
                    print(f"⚠️ Could not update embed: {e}")

                wait_em = make_embed(
                    title="⏳  Added to Waiting List",
                    description=(
                        f"**{name}**, registration is full!\n"
                        f"You're **#{position}** on the waiting list.\n"
                        f"If someone leaves, you'll be promoted automatically."
                    ),
                    color=EMBED_COLOR_WARN,
                )
                temp = await channel.send(embed=wait_em)
                await asyncio.sleep(15)
                try:
                    await temp.delete()
                except discord.NotFound:
                    pass


# =========================
# 🔄 REACTION REMOVE (auto-promote)
# =========================

@bot.event
async def on_raw_reaction_remove(payload):
    """When someone un-reacts, remove them, add to cancelled list, and auto-promote from waiting list."""
    if payload.user_id == bot.user.id:
        return

    ch_id = payload.channel_id
    if ch_id not in active_sessions:
        return

    session = active_sessions[ch_id]
    if payload.message_id != session["message_id"]:
        return
    if str(payload.emoji) != REGISTER_EMOJI:
        return

    uid     = payload.user_id
    channel = bot.get_channel(ch_id)

    if uid in session["confirmed"]:
        session["confirmed"].remove(uid)

        # Mark as cancelled so they can't re-register
        if uid not in session["cancelled_users"]:
            session["cancelled_users"].append(uid)

        # Promote first person from waiting list
        if session["waiting_list"]:
            promoted_uid = session["waiting_list"].pop(0)
            session["confirmed"].append(promoted_uid)
            all_time_leaderboard[promoted_uid] += 1

            if channel:
                promo_name = _member_name(channel, promoted_uid)
                notify_em = make_embed(
                    title="🎉  Promoted from Waiting List!",
                    description=f"**{promo_name}**, a slot opened up — you are now **confirmed**!",
                    color=EMBED_COLOR_SUCCESS,
                )
                temp = await channel.send(embed=notify_em)
                await asyncio.sleep(10)
                try:
                    await temp.delete()
                except discord.NotFound:
                    pass

                # Also DM the promoted user
                try:
                    promoted_member = channel.guild.get_member(promoted_uid)
                    if promoted_member:
                        dm_em = make_embed(
                            title="🎉  You've Been Promoted!",
                            description=f"A slot opened up in **{session['event_name']}** — you are now **confirmed**!",
                            color=EMBED_COLOR_SUCCESS,
                        )
                        await promoted_member.send(embed=dm_em)
                except discord.Forbidden:
                    pass

    elif uid in session["waiting_list"]:
        session["waiting_list"].remove(uid)

        # Mark as cancelled so they can't re-register
        if uid not in session["cancelled_users"]:
            session["cancelled_users"].append(uid)

    # Also remove from pending tickets
    session["pending_tickets"].discard(uid)

    # Update embed
    if channel:
        try:
            msg = await channel.fetch_message(session["message_id"])
            await msg.edit(embed=build_session_embed(session))
        except Exception:
            pass


# =========================
# 📨 MESSAGE HANDLER
# =========================

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot:
        return

    all_ch_ids = set(CHANNEL_IDS.values()) - {0}
    if message.channel.id not in all_ch_ids:
        return
    if message.content.startswith("!"):
        return

    ch_id = message.channel.id
    if ch_id in active_sessions:
        em = make_embed(
            title="👆  React to Register!",
            description=(
                f"Don't type — **react with {REGISTER_EMOJI}** on the session message above!\n"
                "That's how you claim a slot."
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
# ============================================================
# 🎮  COMMANDS
# ============================================================

# ---------- !help  (Command Center) ----------

def build_help_page(key, ctx):
    """Generate a list of embeds for a given help category."""
    now = datetime.now(UK_TZ)

    if key == "home":
        # ── Dynamic stats ──
        member_count = ctx.guild.member_count if ctx.guild else "?"
        session_count = len(active_sessions)
        uptime_str = "Just started"
        if bot_start_time:
            delta = datetime.now(UK_TZ) - bot_start_time
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            if hours > 0:
                uptime_str = f"{hours}h {minutes}m"
            else:
                uptime_str = f"{minutes}m"

        # ── Main Command Center Embed ──
        em = discord.Embed(
            title="✦  SARKAR COMMAND CENTER  ✦",
            description=(
                "Welcome to the **Sarkar Family Bot** — your all-in-one "
                "event automation & management system.\n\n"
                "Use the **dropdown** below to explore:\n"
                "╔══════════════════════════════════════╗\n"
                "║  🎮  **Events & Registration**       ║\n"
                "║  🛡️  **Admin & Moderation**           ║\n"
                "║  ℹ️  **General & Fun**                ║\n"
                "╚══════════════════════════════════════╝"
            ),
            color=EMBED_COLOR,
            timestamp=now,
        )
        em.add_field(name="👥 Members", value=f"**{member_count}**", inline=True)
        em.add_field(name="📡 Active Sessions", value=f"**{session_count}**", inline=True)
        em.add_field(name="⏱️ Uptime", value=f"**{uptime_str}**", inline=True)
        em.add_field(name="🕒 UK Time", value=f"**{now.strftime('%H:%M')}**", inline=True)
        em.add_field(name="🔧 Prefix", value="**!**", inline=True)
        em.add_field(name="📖 Commands", value="**14**", inline=True)
        em.set_footer(text="Sarkar Command Center  ✦  Select a category below")

        # ── GIF inside the embed (single block) ──
        help_gif = get_bot_gif("HELP_GIF")
        if help_gif:
            em.set_image(url=help_gif)

        return [em]

    if key == "events":
        em = discord.Embed(
            title="🎮  Events & Registration",
            description=(
                "All commands for events, schedules, and signups.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "```\n"
                "Command        Aliases          Description\n"
                "────────────── ──────────────── ──────────────────────────────\n"
                "!events        !schedule        Full event schedule table\n"
                "!status        —                Live sessions & upcoming\n"
                "!registrations !regs, !list     Confirmed & waiting lists\n"
                "!raid          —                🚨 Trigger Family Raid alert\n"
                "!robbery       —                Open Store Robbery signup\n"
                "```\n"
            ),
            color=0x34D399,
            timestamp=now,
        )
        em.add_field(
            name="📌 How Registration Works",
            value=(
                "```\n"
                "Step  Action\n"
                "───── ────────────────────────────────────────\n"
                " 1    Events open automatically at set times\n"
                " 2    React with 🎟️ on the embed to join\n"
                " 3    Full? You're added to the waiting list\n"
                " 4    Remove your reaction to cancel\n"
                " 5    Waitlist auto-promotes when slot opens\n"
                "```"
            ),
            inline=False,
        )
        em.add_field(
            name="📊 Right Now",
            value=f"🟢 **{len(active_sessions)}** active session(s)",
            inline=True,
        )
        em.set_footer(text="Sarkar Command Center  ✦  Events & Registration")
        return [em]


    if key == "admin":
        em = discord.Embed(
            title="🛡️  Admin & Moderation",
            description=(
                "Commands for admins and moderators.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "```\n"
                "Command        Aliases          Permission       Description\n"
                "────────────── ──────────────── ──────────────── ──────────────────────────\n"
                "!announcement  —                Administrator    Rich text announcement\n"
                "!pager         —                Administrator    Family pager messages\n"
                "!start         —                Administrator    Interactive session creator\n"
                "!close         —                Administrator    Force-close session\n"
                "!raid          —                Administrator    Family Raid alert\n"
                "!robbery       —                Administrator    Store Robbery signup\n"
                "!clean         !purge, !clear   Manage Messages  Purge messages (max 500)\n"
                "!ban           —                Ban Members      Interactive ban system\n"
                "```\n"
            ),
            color=EMBED_COLOR_WARN,
            timestamp=now,
        )
        em.add_field(
            name="⚙️ Feature Details",
            value=(
                "```\n"
                "Feature           Details\n"
                "───────────────── ─────────────────────────────────\n"
                "!start            Event · Limit · Timer · GIF select\n"
                "!announcement     Templates · Formatting · Media\n"
                "!pager            6 types · Send up to 2 at once\n"
                "!ban              Delete msgs → Timeframe → Execute\n"
                "Auto-Clean        All event channels purged every 24h\n"
                "```"
            ),
            inline=False,
        )
        em.set_footer(text="Sarkar Command Center  ✦  Admin & Moderation")
        return [em]

    if key == "general":
        em = discord.Embed(
            title="ℹ️  General & Fun",
            description=(
                "Commands available to everyone.\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "```\n"
                "Command        Aliases          Description\n"
                "────────────── ──────────────── ──────────────────────────────\n"
                "!help          —                Interactive command center\n"
                "!events        !schedule        Full event schedule table\n"
                "!status        —                Live sessions & upcoming\n"
                "!registrations !regs, !list     Confirmed & waiting lists\n"
                "!leaderboard   —                Top 10 most active members\n"
                "!quote         —                Random motivational quote\n"
                "```\n"
            ),
            color=MUSIC_EMBED_COLOR2,
            timestamp=now,
        )
        em.add_field(
            name="💡 Quick Tips",
            value=(
                "```\n"
                "Tip                              Info\n"
                "──────────────────────────────── ─────────────────────────────\n"
                "!regs                            Quick shortcut for regs\n"
                "!schedule                        Alias for !events\n"
                "!leaderboard                     Tracks all event participation\n"
                "!quote                           API Ninjas + local fallback\n"
                "```"
            ),
            inline=False,
        )
        em.set_footer(text="Sarkar Command Center  ✦  General & Fun")
        return [em]

    return []
class CommandCenterView(discord.ui.View):
    """Interactive Command Center with dropdown + buttons."""

    def __init__(self, ctx):
        super().__init__(timeout=180)  # 3 minute timeout
        self.ctx = ctx
        self.current_page = "home"
        self.message = None

        # ── Category Dropdown ──
        select = discord.ui.Select(
            placeholder="📂 Select a category...",
            options=[
                discord.SelectOption(label="Home",                  value="home",    emoji="🏠", description="Dashboard & live stats"),
                discord.SelectOption(label="Events & Registration", value="events",  emoji="🎮", description="Schedule, signups, raids"),
                discord.SelectOption(label="Admin & Moderation",    value="admin",   emoji="🛡️", description="Ban, clean, sessions"),
                discord.SelectOption(label="General & Fun",         value="general", emoji="ℹ️", description="Help, leaderboard, quotes"),
            ],
            row=0,
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command user can navigate!", ephemeral=True)
            return
        self.current_page = interaction.data["values"][0]
        embed_list = build_help_page(self.current_page, self.ctx)
        await interaction.response.edit_message(content="", embeds=embed_list, view=self)

    @discord.ui.button(label="Home", emoji="🏠", style=discord.ButtonStyle.primary, row=1)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command user can navigate!", ephemeral=True)
            return
        self.current_page = "home"
        embed_list = build_help_page("home", self.ctx)
        await interaction.response.edit_message(content="", embeds=embed_list, view=self)

    @discord.ui.button(label="Close", emoji="🗑️", style=discord.ButtonStyle.danger, row=1)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command user can close!", ephemeral=True)
            return
        await interaction.message.delete()
        self.stop()

    async def on_timeout(self):
        """Disable all components on timeout."""
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                embed_list = build_help_page("home", self.ctx)
                if embed_list:
                    embed_list[-1].set_footer(text="⏰ Menu timed out  •  Use !help to reopen")
                    embed_list[-1].color = 0x6B7280  # Gray out
                await self.message.edit(content="", embeds=embed_list, view=self)
            except (discord.NotFound, discord.HTTPException):
                pass


@bot.command(name="help")
async def help_cmd(ctx):
    view = CommandCenterView(ctx)
    embed_list = build_help_page("home", ctx)
    msg = await ctx.send(content="", embeds=embed_list, view=view)
    view.message = msg
# ---------- !status ----------
@bot.command(name="status")
async def status_cmd(ctx):
    now = datetime.now(UK_TZ)
    current_day = now.weekday()
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # ── RP Factory Reminder Channel Custom Status ──
    rp_factory_ch_id = 1486052630655668294
    if ctx.channel.id == rp_factory_ch_id:
        rp_factory_times = ["10:30", "16:30", "22:30"]
        rp_intervals = [60, 45, 30, 15, 5]
        
        upcoming_reminders = []
        for offset_days in [0, 1]:
            target_date = now + timedelta(days=offset_days)
            for t_str in rp_factory_times:
                evt_h, evt_m = map(int, t_str.split(":"))
                evt_time = datetime(target_date.year, target_date.month, target_date.day, evt_h, evt_m)
                evt_time = UK_TZ.localize(evt_time) if evt_time.tzinfo is None else evt_time
                
                for mins in rp_intervals:
                    rem_time = evt_time - timedelta(minutes=mins)
                    if rem_time > now:
                        upcoming_reminders.append((rem_time, evt_time, mins))
        
        upcoming_reminders.sort(key=lambda x: x[0])
        
        if upcoming_reminders:
            next_rem_time, next_evt_time, mins_before = upcoming_reminders[0]
            diff = next_rem_time - now
            mins_left = int(diff.total_seconds() // 60)
            hours_left = mins_left // 60
            mins_left_mod = mins_left % 60
            
            time_left_str = f"{hours_left}h {mins_left_mod}m" if hours_left > 0 else f"{mins_left_mod}m"
            
            em = make_embed(
                title="🎫  RP TICKET REMINDER",
                description=(
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ **Time left:** {time_left_str}\n"
                    f"🔔 **Reminder details:** {mins_before}m before {next_evt_time.strftime('%H:%M')} event\n"
                    f"━━━━━━━━━━━━━━━━━━"
                ),
                color=EMBED_COLOR
            )
        else:
            em = make_embed(title="🎫  RP TICKET REMINDER", description="No upcoming reminders.", color=EMBED_COLOR)
            
        await ctx.send(embed=em)
        return

    # Section display config: (channel_key, emoji, title, color)
    all_sections = [
        ("INFORMAL",      "🎉", "Informal Section",       0xF472B6),
        ("STATE_CONTROL", "🏛️", "State Control Section",   0x60A5FA),
        ("BIZ_WAR",       "💼", "Biz War Section",         0xFBBF24),
        ("RP_TICKET",     "🎫", "RP Ticket Section",       0xA78BFA),
        ("OTHER_EVENTS",  "📦", "Other Events Section",    0x34D399),
        ("SPECIAL_EVENTS", "🌟", "Special Events",         0x8B5CF6),
    ]

    # Detect which section this channel belongs to
    current_section_key = None
    for ch_key, ch_id in CHANNEL_IDS.items():
        if ch_id == ctx.channel.id:
            current_section_key = ch_key
            break
            
    if ctx.channel.id == SPECIAL_EVENT_CHANNEL_ID:
        current_section_key = "SPECIAL_EVENTS"

    # If in an event channel, only show that section; otherwise show all
    if current_section_key:
        section_config = [s for s in all_sections if s[0] == current_section_key]
    else:
        # User specified "Special Events status section ONLY displays Special Events"
        # We also need to hide Special Events when viewing global status? Let's show all if in a random channel.
        section_config = all_sections

    # Group upcoming events by section
    upcoming_by_section = {key: [] for key, _, _, _ in section_config}
    
    for time_str, name, ch_key, max_p, days, _desc in EVENT_LIST:
        if ch_key not in upcoming_by_section:
            continue
        if days is not None and current_day not in days:
            continue
        evt_h, evt_m = map(int, time_str.split(":"))
        evt_minutes = evt_h * 60 + evt_m
        now_minutes = now.hour * 60 + now.minute
        if evt_minutes > now_minutes:
            diff = evt_minutes - now_minutes
            hours_left = diff // 60
            mins_left = diff % 60
            if hours_left > 0:
                time_left = f"{hours_left}h {mins_left}m"
            else:
                time_left = f"{mins_left}m"
            day_info = f" ({', '.join(day_names[d] for d in days)})" if days else ""
            upcoming_by_section[ch_key].append((time_str, name, time_left, day_info))

    if "SPECIAL_EVENTS" in upcoming_by_section:
        for time_str, name, ch_key, max_p, days, _desc in SPECIAL_EVENT_LIST:
            if days is not None and current_day not in days:
                continue
            evt_h, evt_m = map(int, time_str.split(":"))
            evt_minutes = evt_h * 60 + evt_m
            now_minutes = now.hour * 60 + now.minute
            if evt_minutes > now_minutes:
                diff = evt_minutes - now_minutes
                hours_left = diff // 60
                mins_left = diff % 60
                if hours_left > 0:
                    time_left = f"{hours_left}h {mins_left}m"
                else:
                    time_left = f"{mins_left}m"
                day_info = f" ({', '.join(day_names[d] for d in days)})" if days else ""
                upcoming_by_section["SPECIAL_EVENTS"].append((time_str, name, time_left, day_info))

    # Check for active sessions grouped by section
    active_by_section = {}
    for ch_id, session in active_sessions.items():
        if ch_id == SPECIAL_EVENT_CHANNEL_ID:
            active_by_section["SPECIAL_EVENTS"] = session
            continue
        for ch_key, cid in CHANNEL_IDS.items():
            if cid == ch_id:
                active_by_section[ch_key] = session
                break

    # Header embed
    if current_section_key:
        header_title = f"📊  {section_config[0][1]} {section_config[0][2]} — Status"
    else:
        header_title = "📊  Event Status Dashboard"

    header_em = make_embed(
        title=header_title,
        description=(
            f"🕒 **Current UK Time:** {now.strftime('%H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━━"
        ),
        color=EMBED_COLOR,
    )
    await ctx.send(embed=header_em)

    # Send one embed per section
    for ch_key, emoji, title, color in section_config:
        events = upcoming_by_section[ch_key]
        session = active_by_section.get(ch_key)

        # Active session for this section
        if session:
            ch = bot.get_channel(session["channel_id"])
            ch_name = f"#{ch.name}" if ch else "Unknown"
            c_count = len(session["confirmed"])
            w_count = len(session["waiting_list"])
            max_p = session["max_participants"]

            elapsed = remaining = "—"
            if session["start_time"]:
                delta = datetime.now(UK_TZ) - session["start_time"]
                mins = int(delta.total_seconds() // 60)
                secs = int(delta.total_seconds() % 60)
                elapsed = f"{mins}m {secs}s"
                left = max(0, 480 - int(delta.total_seconds()))
                remaining = f"{left // 60}m {left % 60}s"

            section_text = (
                f"🟢 **REGISTRATION OPEN** in {ch_name}\n\n"
                f"🎯 **Event:** {session['event_name']}\n"
                f"👥 **Confirmed:** {c_count}/{max_p}\n"
                f"🕒 **Waiting:** {w_count}\n"
                f"⏱️ **Elapsed:** {elapsed}  |  **Closes in:** {remaining}"
            )
        # No active session — show upcoming timers
        elif events:
            events.sort(key=lambda x: x[0])
            if ch_key == "INFORMAL":
                t, n, tl, di = events[0]
                section_text = f"🔔 Next portal at **{t}** UK  •  starts in **{tl}**"
            else:
                lines = [f"⏳ **{t}** — {n}{di}  •  starts in **{tl}**"
                         for t, n, tl, di in events[:5]]
                section_text = "\n".join(lines)
                if len(events) > 5:
                    section_text += f"\n*…and {len(events) - 5} more today*"
        else:
            section_text = "*No upcoming events in this section today.*"

        em = discord.Embed(
            title=f"{emoji}  {title}",
            description=section_text,
            color=color,
            timestamp=datetime.now(UK_TZ),
        )
        em.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=em)
# ---------- !registrations ----------
@bot.command(name="registrations", aliases=["list", "regs"])
async def registrations_cmd(ctx):
    ch_id = ctx.channel.id
    if ch_id not in active_sessions:
        em = make_embed(
            title="🔴  No Active Session",
            description="There's no session running in this channel.",
            color=EMBED_COLOR_WARN,
        )
        await ctx.reply(embed=em, mention_author=False)
        return

    session   = active_sessions[ch_id]
    confirmed = session["confirmed"]
    waiting   = session["waiting_list"]
    max_p     = session["max_participants"]

    if confirmed:
        lines = []
        for i, uid in enumerate(confirmed, 1):
            emoji = SLOT_EMOJIS[i - 1] if i <= len(SLOT_EMOJIS) else "🎉"
            lines.append(f"{emoji} **#{i}** — **{_member_name(ctx.channel, uid)}**")
        confirmed_text = "\n".join(lines)
    else:
        confirmed_text = "*No one has registered yet!*"

    fields = [
        ("📝 Confirmed Members", confirmed_text, False),
        ("👥 Confirmed", f"**{len(confirmed)} / {max_p}**", True),
        ("🕒 Waiting", f"**{len(waiting)}**", True),
    ]
    if waiting:
        wl = [f"**#{i}** — {_member_name(ctx.channel, uid)}" for i, uid in enumerate(waiting, 1)]
        fields.append(("⏳ Waiting List", "\n".join(wl), False))

    em = make_embed(
        title=f"📝  {session['event_name']} — Registrations",
        description=f"**{len(confirmed)}/{max_p}** slots confirmed.",
        color=EMBED_COLOR,
        fields=fields,
    )
    await ctx.reply(embed=em, mention_author=False)


# ---------- !events ----------
@bot.command(name="events", aliases=["schedule"])
async def events_cmd(ctx):
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Build event rows per section: (time, name, max_p, day_info)
    sections = {"INFORMAL": [], "STATE_CONTROL": [], "BIZ_WAR": [], "RP_TICKET": [], "OTHER_EVENTS": [], "SPECIAL_EVENTS": []}
    for time_str, name, ch_key, max_p, days, _desc in EVENT_LIST:
        if ch_key not in sections or ch_key == "INFORMAL":
            continue
        day_info = f"({', '.join(day_names[d] for d in days)})" if days else "Daily"
        sections[ch_key].append((time_str, name, max_p, day_info))
        
    for time_str, name, ch_key, max_p, days, _desc in SPECIAL_EVENT_LIST:
        day_info = f"({', '.join(day_names[d] for d in days)})" if days else "Daily"
        sections["SPECIAL_EVENTS"].append((time_str, name, max_p, day_info))

    section_config = [
        ("INFORMAL",      "🎉", "Informal Section",      0xF472B6),
        ("STATE_CONTROL", "🏛️", "State Control Section",  0x60A5FA),
        ("BIZ_WAR",       "💼", "Biz War Section",        0xFBBF24),
        ("RP_TICKET",     "🎫", "RP Ticket Section",      0xA78BFA),
        ("OTHER_EVENTS",  "📦", "Other Events Section",   0x34D399),
        ("SPECIAL_EVENTS","🌟", "Special Events",         0x8B5CF6),
    ]

    # ── Header embed ──
    header_em = make_embed(
        title="📅  Event Schedule (UK Time)",
        description=(
            "Registration polls trigger automatically at these times!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=EMBED_COLOR,
    )
    await ctx.send(embed=header_em)

    # ── Informal (summary) ──
    inf_em = discord.Embed(
        title="🎉  Informal Section",
        description=(
            "```\n"
            "⏰ Time    │ 📋 Event         │ 👥 Slots\n"
            "──────────┼──────────────────┼─────────\n"
            "Every :30 │ 🎉 Informal 🎉   │   10\n"
            "```\n"
            "*Runs every hour, every day (24 sessions/day)*"
        ),
        color=0xF472B6,
        timestamp=datetime.now(UK_TZ),
    )
    inf_em.set_footer(text=FOOTER_TEXT)
    await ctx.send(embed=inf_em)

    # ── Each section as its own embed with table ──
    for ch_key, emoji, title, color in section_config:
        if ch_key == "INFORMAL":
            continue
        events = sections.get(ch_key, [])
        if not events:
            continue

        # Sort by time
        events.sort(key=lambda e: e[0])

        # Build table rows
        header_row = "⏰ Time  │ 📋 Event                        │ 👥 │ 📆 Days"
        sep_row    = "─────────┼─────────────────────────────────┼────┼────────"
        rows = [header_row, sep_row]

        for t, n, mp, di in events:
            # Trim emoji from name for cleaner table
            clean_name = n.ljust(31)[:31]
            rows.append(f"{t}    │ {clean_name} │ {str(mp).rjust(2)} │ {di}")

        # Discord has 4096 char limit for description — chunk if needed
        table_text = "\n".join(rows)
        chunks = []
        current_chunk = []
        current_len = 0
        for row in rows:
            if current_len + len(row) + 1 > 3900:  # Leave room for code block markers
                chunks.append("\n".join(current_chunk))
                current_chunk = [rows[0], rows[1]]  # Re-add header
                current_len = len(rows[0]) + len(rows[1]) + 2
            current_chunk.append(row)
            current_len += len(row) + 1
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        for i, chunk in enumerate(chunks):
            part = f" (Part {i+1})" if len(chunks) > 1 else ""
            em = discord.Embed(
                title=f"{emoji}  {title}{part}",
                description=f"```\n{chunk}\n```",
                color=color,
                timestamp=datetime.now(UK_TZ),
            )
            em.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=em)

    # ── Extra info embed ──
    info_em = make_embed(
        title="📌  Additional Info",
        description=(
            "**🎮 Manual Events**\n"
            "┌─────────────────────────────────────────┐\n"
            "│ **Store Robbery** → `!robbery`          │\n"
            "│ **Family Raid**   → `!raid`             │\n"
            "└─────────────────────────────────────────┘\n\n"
            "**❌ Lose Gun/Ammo on Death:**\n"
            f"> {', '.join(GUN_LOSS_EVENTS)}\n"
            "> *(Safe with Prime Platinum)*\n\n"
            "**✅ Safe Events (No Gun Loss):**\n"
            f"> {', '.join(NO_GUN_LOSS_EVENTS)}"
        ),
        color=EMBED_COLOR,
    )
    await ctx.send(embed=info_em)
# ---------- !raid ----------
@bot.command(name="raid")
@commands.has_permissions(administrator=True)
async def raid_cmd(ctx):
    ch_id = CHANNEL_IDS.get("OTHER_EVENTS", 0)
    if ch_id == 0:
        await ctx.reply("⚠️ OTHER_EVENTS channel not configured!", delete_after=10)
        return

    channel = bot.get_channel(ch_id)
    if channel is None:
        await ctx.reply("⚠️ Could not find the OTHER_EVENTS channel!", delete_after=10)
        return

    em = make_embed(
        title="🚨  FAMILY RAID  🚨",
        description="**EVERYONE COME — WE ARE ON RAID** 🚨\n\nDrop everything and get in NOW!",
        color=EMBED_COLOR_CLOSE,
    )
    await channel.send(embed=em)

    if ctx.channel.id != ch_id:
        await ctx.reply(f"✅ Raid alert sent to <#{ch_id}>!", delete_after=10)


# ---------- !robbery ----------
@bot.command(name="robbery")
@commands.has_permissions(administrator=True)
async def robbery_cmd(ctx):
    ch_id = CHANNEL_IDS.get("OTHER_EVENTS", 0)
    if ch_id == 0:
        await ctx.reply("⚠️ OTHER_EVENTS channel not configured!", delete_after=10)
        return

    if ch_id in active_sessions:
        await ctx.reply("⚠️ A session is already active in that channel!", delete_after=10)
        return

    asyncio.create_task(open_session(ch_id, "Store Robbery", 25))
    await ctx.reply(f"✅ Store Robbery registration opened in <#{ch_id}>!", delete_after=10)


# ---------- !start (Interactive View) ----------

class CustomTimerModal(discord.ui.Modal, title='Custom Session Timer'):
    timer_input = discord.ui.TextInput(
        label='Duration in Minutes',
        placeholder='e.g., 20',
        required=True,
        max_length=4
    )

    def __init__(self, view_ref, check_start_ready_func):
        super().__init__()
        self.view_ref = view_ref
        self.check_start_ready = check_start_ready_func

    async def on_submit(self, interaction: discord.Interaction):
        val = self.timer_input.value.strip()
        if not val.isdigit():
            await interaction.response.send_message("⚠️ Please enter a valid number of minutes.", ephemeral=True)
            return
        
        minutes = int(val)
        if minutes <= 0:
            await interaction.response.send_message("⚠️ Duration must be greater than 0.", ephemeral=True)
            return

        self.view_ref.selected_timer_seconds = minutes * 60
        self.view_ref.custom_timer_str = f"{minutes} minutes"
        
        await interaction.response.edit_message(view=self.view_ref)
        await self.check_start_ready(interaction)

class InteractiveStartView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=180) # 3 minutes strictly for admin setup
        self.ctx = ctx
        self.selected_event = None
        self.selected_limit = None
        self.selected_timer_seconds = None
        self.custom_timer_str = None
        self.selected_gif = None

        # Gather all distinct event names
        all_event_names = {e[1] for e in EVENT_LIST} | {e[1] for e in SPECIAL_EVENT_LIST}
        event_options = [discord.SelectOption(label=name) for name in sorted(list(all_event_names))]
        
        # Build Dropdown 1: Event
        self.event_select = discord.ui.Select(
            placeholder="1) Choose Event Name...",
            options=event_options,
            min_values=1,
            max_values=1,
            row=0
        )
        self.event_select.callback = self.event_select_callback
        self.add_item(self.event_select)

        # Build Dropdown 2: Limit
        limit_options = [discord.SelectOption(label=str(i), value=str(i)) for i in [10, 15, 20, 25, 30]]
        self.limit_select = discord.ui.Select(
            placeholder="2) Choose Max Members...",
            options=limit_options,
            min_values=1,
            max_values=1,
            row=1
        )
        self.limit_select.callback = self.limit_select_callback
        self.add_item(self.limit_select)

        # Build Dropdown 3: Timer
        timer_options = [
            discord.SelectOption(label="5 minutes", value="300"),
            discord.SelectOption(label="10 minutes", value="600"),
            discord.SelectOption(label="15 minutes", value="900"),
            discord.SelectOption(label="30 minutes", value="1800"),
            discord.SelectOption(label="1 hour", value="3600"),
            discord.SelectOption(label="Custom Time...", value="custom"),
        ]
        self.timer_select = discord.ui.Select(
            placeholder="3) Choose Close Timer...",
            options=timer_options,
            min_values=1,
            max_values=1,
            row=2
        )
        self.timer_select.callback = self.timer_select_callback
        self.add_item(self.timer_select)

        # Build Dropdown 4: Custom GIF
        gif_options = [discord.SelectOption(label="No Custom GIF (Use Default)", value="none")]
        try:
            with open("config/eventGifs.json", "r", encoding="utf-8") as f:
                gifs = json.load(f)
                # Ensure unique values by using the event key name!
                for key in gifs.keys():
                    gif_options.append(discord.SelectOption(label=key, value=key[:100]))
        except Exception:
            pass
        # Only take up to 25 options to respect discord limit
        gif_options = gif_options[:25]
        self.gif_select = discord.ui.Select(
            placeholder="4) Optional: Choose Custom GIF...",
            options=gif_options,
            min_values=1,
            max_values=1,
            row=3
        )
        self.gif_select.callback = self.gif_select_callback
        self.add_item(self.gif_select)

    async def check_start_ready(self, interaction: discord.Interaction):
        # If the required three are populated, we can launch the session
        if self.selected_event and self.selected_limit and self.selected_timer_seconds:
            # Check if channel is proper
            ch_id = self.ctx.channel.id
            all_ch_ids = set(CHANNEL_IDS.values()) | {SPECIAL_EVENT_CHANNEL_ID} - {0}
            
            # Disable components and update user
            for child in self.children:
                child.disabled = True
            
            try:
                if not interaction.response.is_done():
                    await interaction.response.edit_message(content="⏳ Launching session...", view=self)
                else:
                    await interaction.message.edit(content="⏳ Launching session...", view=self)
            except discord.NotFound:
                pass

            if ch_id not in all_ch_ids:
                await self.ctx.reply("⚠️ This channel is not a registered event channel!", delete_after=10)
                return

            if ch_id in active_sessions:
                await self.ctx.reply("⚠️ A session is already active in this channel!", delete_after=10)
                return

            # Resolve GIF selected (it's the key name, not the URL directly anymore!)
            final_custom_gif_url = None
            if self.selected_gif and self.selected_gif != "none":
                try:
                    with open("config/eventGifs.json", "r", encoding="utf-8") as f:
                        gifs = json.load(f)
                        if self.selected_gif in gifs:
                            final_custom_gif_url = gifs[self.selected_gif]
                except Exception:
                    pass

            # Open session with custom timer
            asyncio.create_task(open_session(
                target_channel_id=ch_id, 
                event_name=self.selected_event, 
                max_participants=self.selected_limit,
                custom_timer_seconds=self.selected_timer_seconds,
                custom_gif=final_custom_gif_url
            ))
            
            timer_text = self.custom_timer_str if self.custom_timer_str else f"{self.selected_timer_seconds // 60} minutes"
            gif_text = self.selected_gif if self.selected_gif and self.selected_gif != "none" else "Auto/None"
            await self.ctx.reply(f"✅ Session for **{self.selected_event}** started (Limit: {self.selected_limit}, Timer: {timer_text}, Custom GIF: {gif_text})!", delete_after=10)
            
            # Cleanup the configurator UI
            await asyncio.sleep(2)
            try:
                await interaction.message.delete()
            except discord.NotFound:
                pass


    async def event_select_callback(self, interaction: discord.Interaction):
        self.selected_event = self.event_select.values[0]
        self.event_select.placeholder = f"Event: {self.selected_event}"
        await interaction.response.edit_message(view=self)
        await self.check_start_ready(interaction)

    async def limit_select_callback(self, interaction: discord.Interaction):
        self.selected_limit = int(self.limit_select.values[0])
        self.limit_select.placeholder = f"Limit: {self.selected_limit} Members"
        await interaction.response.edit_message(view=self)
        await self.check_start_ready(interaction)

    async def timer_select_callback(self, interaction: discord.Interaction):
        val = self.timer_select.values[0]
        if val == "custom":
            self.timer_select.placeholder = "Timer: Custom..."
            # Trigger modal input for custom time
            await interaction.response.send_modal(CustomTimerModal(self, self.check_start_ready))
        else:
            self.selected_timer_seconds = int(val)
            self.custom_timer_str = None
            minutes = self.selected_timer_seconds // 60
            self.timer_select.placeholder = f"Timer: {minutes} minutes"
            await interaction.response.edit_message(view=self)
            await self.check_start_ready(interaction)

    async def gif_select_callback(self, interaction: discord.Interaction):
        val = self.gif_select.values[0]
        self.selected_gif = val
        self.gif_select.placeholder = f"GIF: {'Default' if val == 'none' else 'Custom Selected'}"
        await interaction.response.edit_message(view=self)
        await self.check_start_ready(interaction)


@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start_cmd(ctx):
    view = InteractiveStartView(ctx)
    em = discord.Embed(
        title="⚙️ Manual Session Creator",
        description="Select the event details below to start a custom session.",
        color=EMBED_COLOR
    )
    await ctx.reply(embed=em, view=view)


# ---------- !close ----------
@bot.command(name="close")
@commands.has_permissions(administrator=True)
async def close_cmd(ctx):
    ch_id = ctx.channel.id
    if ch_id not in active_sessions:
        await ctx.reply("⚠️ No active session in this channel!", delete_after=10)
        return

    await close_session(ch_id)
    await ctx.reply("✅ Session closed!", delete_after=10)



# ---------- !pager ----------

class PagerMessageSelect(discord.ui.Select):
    def __init__(self, msg_type: str):
        self.msg_type = msg_type
        options = []
        for i, text in enumerate(PAGER_MESSAGES[msg_type][:25]):
            # Use the first 100 chars as the label
            label = text[:97] + "..." if len(text) > 100 else text
            options.append(discord.SelectOption(label=label, value=str(i)))

        super().__init__(
            placeholder="Select Pager Message (Max 2)",
            min_values=1,
            max_values=min(2, len(options)),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # We need to grab the actual message text from the selected indices
        selected_texts = [PAGER_MESSAGES[self.msg_type][int(idx)] for idx in self.values]

        target_channel = interaction.client.get_channel(PAGER_CHANNEL_ID)
        if not target_channel:
            await interaction.response.send_message("❌ Pager channel not found!", ephemeral=True)
            return

        for text in selected_texts:
            em = make_embed(
                title="📟 Pager Message",
                description=f"<@&{FAMILY_ROLE_ID}>\n\n**{text}**",
                color=EMBED_COLOR_WARN,
            )
            await target_channel.send(embed=em)

        await interaction.response.edit_message(
            content=f"✅ Sent {len(selected_texts)} {self.msg_type} message(s) to <#{PAGER_CHANNEL_ID}>!",
            embed=None,
            view=None
        )


class PagerTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Serious", value="Serious", emoji="⚠️"),
            discord.SelectOption(label="Motivational", value="Motivational", emoji="💪"),
            discord.SelectOption(label="Funny", value="Funny", emoji="😂"),
            discord.SelectOption(label="Aggressive / Hype", value="Hype", emoji="⚡"),
            discord.SelectOption(label="Threat / Warning", value="Threat", emoji="🚨"),
            discord.SelectOption(label="Chill / Friendly", value="Chill", emoji="📢"),
        ]
        super().__init__(
            placeholder="Select Pager Message Type",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_type = self.values[0]
        
        # Create a new view with the specific messages for that type
        view = discord.ui.View(timeout=180)
        view.add_item(PagerMessageSelect(selected_type))
        
        em = make_embed(
            title=f"📟 Select {selected_type} Messages",
            description="Choose up to 2 specific messages to send to the family.",
            color=EMBED_COLOR
        )
        
        await interaction.response.edit_message(embed=em, view=view)


class PagerView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.add_item(PagerTypeSelect())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command user can interact with this menu!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            # We fetch the message we attached this view to
            if hasattr(self, "message") and self.message:
                await self.message.edit(view=self)
        except Exception:
            pass


@bot.command(name="pager")
@commands.has_permissions(administrator=True)
async def pager_cmd(ctx):
    view = PagerView(ctx)
    em = make_embed(
        title="📟 Pager System",
        description="Select the type of pager message you want to send out to the family.",
        color=EMBED_COLOR
    )
    msg = await ctx.reply(embed=em, view=view, mention_author=False)
    view.message = msg


# ---------- !announcement ----------
ANNOUNCEMENT_CHANNELS = {
    "Announcement Section": 1476284162737700915,
    "Fam Announcement": 1476284338889822208,
    "Turf Announcement": 1467862732786110699
}

class AnnouncementFormatStyleView(discord.ui.View):
    """View to select the style for a selected word/sentence."""
    def __init__(self, main_view, selected_text: str):
        super().__init__(timeout=180)
        self.main_view = main_view
        self.selected_text = selected_text

    async def apply_format(self, interaction: discord.Interaction, formatted_text: str):
        # Replace the literal text in the main body with the formatted text
        if self.selected_text in self.main_view.body_text:
            self.main_view.body_text = self.main_view.body_text.replace(self.selected_text, formatted_text, 1)
        else:
            await interaction.response.send_message("⚠️ Could not find that exact text in the message.", ephemeral=True)
            return

        if not interaction.response.is_done():
            await interaction.response.defer()

        # Delete this sub-view message
        await interaction.message.delete()
        # Refresh the main view
        await self.main_view.refresh_ui()

    @discord.ui.button(label="Bold (Highlight)", style=discord.ButtonStyle.secondary)
    async def btn_bold(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_format(interaction, f"**{self.selected_text}**")

    @discord.ui.button(label="Inline Code (Highlight)", style=discord.ButtonStyle.secondary)
    async def btn_code(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_format(interaction, f"`{self.selected_text}`")
        
    @discord.ui.button(label="🔴 Red", style=discord.ButtonStyle.danger)
    async def btn_red(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_format(interaction, f"```ansi\n\u001b[0;31m{self.selected_text}\u001b[0m\n```")

    @discord.ui.button(label="🟢 Green", style=discord.ButtonStyle.success)
    async def btn_green(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_format(interaction, f"```ansi\n\u001b[0;32m{self.selected_text}\u001b[0m\n```")

    @discord.ui.button(label="🔵 Blue", style=discord.ButtonStyle.primary)
    async def btn_blue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_format(interaction, f"```ansi\n\u001b[0;34m{self.selected_text}\u001b[0m\n```")

    @discord.ui.button(label="🟡 Yellow", style=discord.ButtonStyle.secondary)
    async def btn_yellow(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_format(interaction, f"```ansi\n\u001b[0;33m{self.selected_text}\u001b[0m\n```")

    @discord.ui.button(label="🟣 Purple", style=discord.ButtonStyle.secondary)
    async def btn_purple(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apply_format(interaction, f"```ansi\n\u001b[0;35m{self.selected_text}\u001b[0m\n```")


class AnnouncementFormatTextModal(discord.ui.Modal, title='Select Text to Format'):
    text_input = discord.ui.TextInput(
        label='Enter exact word/sentence to format:',
        placeholder='Must match exactly what is in the message',
        required=True,
        max_length=150
    )

    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view

    async def on_submit(self, interaction: discord.Interaction):
        selected_text = self.text_input.value
        if selected_text not in self.main_view.body_text:
            await interaction.response.send_message("⚠️ That text was not found in the current message body.", ephemeral=True)
            return

        style_view = AnnouncementFormatStyleView(self.main_view, selected_text)
        await interaction.response.send_message(
            f"Select formatting for: **{selected_text}**", 
            view=style_view, 
            ephemeral=True
        )


class AnnouncementTitleModal(discord.ui.Modal, title='Set Announcement Title'):
    title_input = discord.ui.TextInput(
        label='Announcement Title',
        placeholder='e.g., 🚨 EVENT ANNOUNCEMENT',
        required=True,
        max_length=100
    )

    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view

    async def on_submit(self, interaction: discord.Interaction):
        self.main_view.title_text = self.title_input.value
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.main_view.refresh_ui()


class AnnouncementBuilderView(discord.ui.View):
    def __init__(self, ctx, announcement_message, initial_body: str):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.announcement_message = announcement_message
        self.builder_message = None
        
        self.title_text = "🚨 ANNOUNCEMENT"
        self.body_text = initial_body
        self.target_channel_id = ctx.channel.id
        self.selected_roles = []
        
        # New Advanced Properties
        self.ping_type = "none" # "none", "here", "everyone", "roles"
        self.media_url = None
        self.add_reactions = False
        self.schedule_time_str = None
        
        # Undo / Redo History Stack
        self.history = [initial_body]
        self.history_index = 0

        # Row 0: Editor Tools
        tools_options = [
            discord.SelectOption(label="Append Bold Text", value="bold", emoji="🅱️"),
            discord.SelectOption(label="Append Italic Text", value="italic", emoji="🇮"),
            discord.SelectOption(label="Append Heading", value="heading", emoji="🏷️"),
            discord.SelectOption(label="Append Quote", value="quote", emoji="💬"),
            discord.SelectOption(label="Append Code Block", value="code", emoji="💻"),
            discord.SelectOption(label="Append Bullet List", value="bullet", emoji="•"),
            discord.SelectOption(label="Append Numbered List", value="number", emoji="1️⃣"),
            discord.SelectOption(label="Insert Divider", value="divider", emoji="➖"),
            discord.SelectOption(label="Edit Raw Markdown", value="raw", emoji="📝"),
            discord.SelectOption(label="Attach Media URL", value="media", emoji="🖼️"),
            discord.SelectOption(label="Toggle Reactions", value="reactions", emoji="👍"),
            discord.SelectOption(label="Save as Template", value="template", emoji="💾"),
            discord.SelectOption(label="Schedule Send", value="schedule", emoji="⏰"),
        ]
        self.tools_select = discord.ui.Select(
            custom_id="ann_tools",
            placeholder="🛠️ Editor & Settings Toolbar...",
            options=tools_options,
            min_values=1, max_values=1, row=0
        )
        self.tools_select.callback = self.tools_select_callback
        self.add_item(self.tools_select)

        # Row 1: Channel
        ch_options = [discord.SelectOption(label="Current Channel", value=str(ctx.channel.id))]
        for name, cid in ANNOUNCEMENT_CHANNELS.items():
            if cid != ctx.channel.id:
                ch_options.append(discord.SelectOption(label=name, value=str(cid)))
                
        self.channel_select = discord.ui.Select(
            custom_id="ann_channel",
            placeholder="📍 Move to Channel (Optional)",
            options=ch_options,
            min_values=1, max_values=1, row=1
        )
        self.channel_select.callback = self.channel_select_callback
        self.add_item(self.channel_select)

        # Row 2: Ping Options
        ping_options = [
            discord.SelectOption(label="No Ping", value="none", emoji="🔇"),
            discord.SelectOption(label="@here", value="here", emoji="🔔"),
            discord.SelectOption(label="@everyone", value="everyone", emoji="🌍"),
            discord.SelectOption(label="Specific Roles", value="roles", emoji="👥"),
        ]
        self.ping_select = discord.ui.Select(
            custom_id="ann_ping",
            placeholder="🔔 Ping Options (Default: No Ping)",
            options=ping_options,
            min_values=1, max_values=1, row=2
        )
        self.ping_select.callback = self.ping_select_callback
        self.add_item(self.ping_select)

        # Row 3: Role Select (Cached)
        self.role_select_item = discord.ui.RoleSelect(
            custom_id="ann_role",
            placeholder="👥 Select Roles to Ping...",
            min_values=1, max_values=15, row=3
        )
        self.role_select_item.callback = self.role_select_callback

    def push_history(self, new_text):
        if new_text == self.body_text:
            return
        self.history = self.history[:self.history_index + 1]
        self.history.append(new_text)
        self.history_index += 1
        self.body_text = new_text

    async def tools_select_callback(self, interaction: discord.Interaction):
        val = self.tools_select.values[0]
        
        if val == "bold":
            await interaction.response.send_modal(AppendTextModal(self, "bold", "Append Bold Text", "Enter text to bold"))
        elif val == "italic":
            await interaction.response.send_modal(AppendTextModal(self, "italic", "Append Italic Text", "Enter text to italicize"))
        elif val == "heading":
            await interaction.response.send_modal(AppendTextModal(self, "heading", "Append Heading", "Enter heading text"))
        elif val == "quote":
            await interaction.response.send_modal(AppendTextModal(self, "quote", "Append Quote", "Enter quote block text"))
        elif val == "code":
            await interaction.response.send_modal(AppendTextModal(self, "code", "Append Code Block", "Enter code block contents"))
        elif val == "bullet":
            await interaction.response.send_modal(AppendTextModal(self, "bullet", "Append Bullet List", "Enter line items"))
        elif val == "number":
            await interaction.response.send_modal(AppendTextModal(self, "number", "Append Numbered List", "Enter line items"))
        elif val == "divider":
            new_text = self.body_text + ("\n━━━━━━━━━━━━━━━━━━━━\n" if not self.body_text.endswith('\n') else "━━━━━━━━━━━━━━━━━━━━\n")
            self.push_history(new_text)
            if not interaction.response.is_done():
                await interaction.response.defer()
            await self.refresh_ui()
        elif val == "raw":
            await interaction.response.send_modal(RawTextModal(self))
        elif val == "media":
            await interaction.response.send_modal(AnnouncementMediaModal(self))
        elif val == "reactions":
            self.add_reactions = not self.add_reactions
            if not interaction.response.is_done():
                await interaction.response.defer()
            await self.refresh_ui()
        elif val == "template":
            await interaction.response.send_modal(AnnouncementTemplateModal(self))
        elif val == "schedule":
            await interaction.response.send_modal(AnnouncementScheduleModal(self))

    def generate_announcement_embeds(self):
        embeds_list = []
        gif_url = get_bot_gif("ANNOUNCEMENT_GIF")
        if gif_url:
            gif_em = discord.Embed(color=EMBED_COLOR)
            gif_em.set_image(url=gif_url)
            embeds_list.append(gif_em)

        em = discord.Embed(
            title=self.title_text,
            description=self.body_text,
            color=EMBED_COLOR,
            timestamp=datetime.now(UK_TZ)
        )
        em.set_footer(text=FOOTER_TEXT)
        
        # Inject Media Image if attached
        if self.media_url:
            em.set_image(url=self.media_url)
            
        embeds_list.append(em)
        return embeds_list

    def generate_announcement_content(self):
        content_lines = []
        
        if self.ping_type == "here":
            content_lines.append("@here")
        elif self.ping_type == "everyone":
            content_lines.append("@everyone")
        elif self.ping_type == "roles" and self.selected_roles:
            mention_str = " ".join(r.mention for r in self.selected_roles)
            content_lines.append(mention_str)
            
        return "\n".join(content_lines)

    async def refresh_ui(self):
        # 1. Update the live announcement message itself
        ann_content = self.generate_announcement_content()
        ann_embeds = self.generate_announcement_embeds()
        
        try:
            await self.announcement_message.edit(content=ann_content, embeds=ann_embeds)
        except Exception as e:
            print(f"Error updating announcement message: {e}")

        # 2. Update the Builder Panel message
        ping_display = self.ping_type.title()
        if self.ping_type == "roles":
            ping_display = ", ".join(r.mention for r in self.selected_roles) if self.selected_roles else "None selected"
        elif self.ping_type == "here":
            ping_display = "@here"
        elif self.ping_type == "everyone":
            ping_display = "@everyone"
            
        builder_desc = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "**📝 Channel:** " + f"<#{self.target_channel_id}>\n"
            f"**🔔 Pings:** {ping_display}\n"
            f"**🖼️ Media:** {'Attached' if self.media_url else 'None'}\n"
            f"**⏰ Schedule:** {self.schedule_time_str if self.schedule_time_str else 'Send Now'}\n"
            f"**🏷️ Reactions:** {'Yes' if self.add_reactions else 'No'}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        
        preview_em = discord.Embed(
            title="🛠️ Advanced Announcement Builder",
            description=builder_desc,
            color=0x818CF8
        )
        
        if self.builder_message:
            await self.builder_message.edit(embed=preview_em, view=self)

    async def channel_select_callback(self, interaction: discord.Interaction):
        self.target_channel_id = int(self.channel_select.values[0])
        for opt in self.channel_select.options:
            if opt.value == str(self.target_channel_id):
                self.channel_select.placeholder = f"Target: {opt.label}"
                break
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.refresh_ui()

    async def ping_select_callback(self, interaction: discord.Interaction):
        self.ping_type = self.ping_select.values[0]
        
        for opt in self.ping_select.options:
            if opt.value == self.ping_type:
                self.ping_select.placeholder = f"Ping: {opt.label}"
                break
                
        # Dynamically show/hide the Role Selector
        if self.ping_type == "roles":
            if self.role_select_item not in self.children:
                self.add_item(self.role_select_item)
        else:
            self.selected_roles = []
            if self.role_select_item in self.children:
                self.remove_item(self.role_select_item)
            
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        if self.builder_message:
            await self.builder_message.edit(view=self)

        await self.refresh_ui()

    async def role_select_callback(self, interaction: discord.Interaction):
        self.selected_roles = self.role_select_item.values
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.refresh_ui()

    @discord.ui.button(label="Undo", emoji="↺", style=discord.ButtonStyle.secondary, row=4)
    async def btn_undo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.history_index > 0:
            self.history_index -= 1
            self.body_text = self.history[self.history_index]
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.refresh_ui()

    @discord.ui.button(label="Redo", emoji="↻", style=discord.ButtonStyle.secondary, row=4)
    async def btn_redo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.body_text = self.history[self.history_index]
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.refresh_ui()

    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.danger, row=4)
    async def btn_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.announcement_message.delete()
        except Exception:
            pass
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="❌ Announcement creation cancelled.", embed=None, view=None)

    @discord.ui.button(label="FINALIZE ANNOUNCEMENT", emoji="✅", style=discord.ButtonStyle.success, row=4)
    async def btn_send(self, interaction: discord.Interaction, button: discord.ui.Button):
        target_ch = self.ctx.guild.get_channel(self.target_channel_id)
        if not target_ch:
            await interaction.response.send_message("⚠️ The selected target channel could not be found.", ephemeral=True)
            return

        # Prepare Content
        ann_content = self.generate_announcement_content()
        ann_embeds = self.generate_announcement_embeds()
        
        # Scheduling Logic
        if self.schedule_time_str:
            try:
                # Parse UK time
                now = datetime.now(UK_TZ)
                target_time = datetime.strptime(self.schedule_time_str, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day, tzinfo=UK_TZ
                )
                if target_time < now:
                    target_time = target_time.replace(day=now.day + 1) # Next day if time already passed
                
                delay_secs = (target_time - now).total_seconds()
                
                async def scheduled_send():
                    await asyncio.sleep(delay_secs)
                    msg = await target_ch.send(content=ann_content, embeds=ann_embeds)
                    if self.add_reactions:
                        for emoji in ["👍", "🔥", "❓"]:
                            await msg.add_reaction(emoji)
                            
                bot.loop.create_task(scheduled_send())
                msg_reply = f"✅ Announcement scheduled to send in <#{self.target_channel_id}> at {self.schedule_time_str} UK Time!"
                
            except ValueError:
                await interaction.response.send_message("⚠️ Invalid time format. Please use HH:MM.", ephemeral=True)
                return
        else:
            # Immediate Send
            msg = await target_ch.send(content=ann_content, embeds=ann_embeds)
            
            # Reactions
            if self.add_reactions:
                for emoji in ["👍", "🔥", "❓"]:
                    await msg.add_reaction(emoji)
                    
            msg_reply = f"✅ Announcement finalized in <#{self.target_channel_id}>!"

        # Delete the drafted message from the current channel
        try:
            await self.announcement_message.delete()
        except Exception:
            pass
            
        # Logging System
        if ANNOUNCEMENT_LOG_CHANNEL_ID != 0:
            log_ch = self.ctx.guild.get_channel(ANNOUNCEMENT_LOG_CHANNEL_ID)
            if log_ch:
                log_em = discord.Embed(
                    title="📝 Announcement Sent",
                    color=discord.Color.gold(),
                    timestamp=datetime.now(UK_TZ)
                )
                log_em.add_field(name="Author", value=interaction.user.mention, inline=True)
                log_em.add_field(name="Channel", value=f"<#{self.target_channel_id}>", inline=True)
                log_em.add_field(name="Scheduled", value=self.schedule_time_str if self.schedule_time_str else "Immediate", inline=True)
                log_em.description = f"**Title:** {self.title_text}\n**Body Snippet:** {self.body_text[:200]}..."
                await log_ch.send(embed=log_em)

        # Disable builder UI and edit the builder message to a success note
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(content=msg_reply, embed=None, view=None)


# ============================================================
# ADVANCED ANNOUNCEMENT SYSTEM DASHBOARD
# ============================================================

class AnnouncementCreateModal(discord.ui.Modal, title="Create New Announcement"):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        
        self.ann_title = discord.ui.TextInput(
            label="Announcement Heading",
            style=discord.TextStyle.short,
            placeholder="🚨 ANNOUNCEMENT",
            default="🚨 ANNOUNCEMENT",
            required=True,
            max_length=256
        )
        self.add_item(self.ann_title)
        
        self.ann_body = discord.ui.TextInput(
            label="Paragraph Input",
            style=discord.TextStyle.paragraph,
            placeholder="Type your main announcement text here...",
            required=True,
            max_length=4000
        )
        self.add_item(self.ann_body)

    async def on_submit(self, interaction: discord.Interaction):
        # We need to spawn the Builder Session with the provided text
        await interaction.response.defer()
        
        gif_url = get_bot_gif("ANNOUNCEMENT_GIF")
        embeds_list = []
        if gif_url:
            gif_em = discord.Embed(color=EMBED_COLOR)
            gif_em.set_image(url=gif_url)
            embeds_list.append(gif_em)

        em = discord.Embed(
            title=self.ann_title.value,
            description=self.ann_body.value,
            color=EMBED_COLOR,
            timestamp=datetime.now(UK_TZ)
        )
        em.set_footer(text=FOOTER_TEXT)
        embeds_list.append(em)
        
        msg = await interaction.channel.send(content="", embeds=embeds_list)
        view = AnnouncementBuilderView(self.ctx, msg, self.ann_body.value)
        view.title_text = self.ann_title.value
        
        builder_desc = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "**📝 Current Channel:** " + f"<#{view.target_channel_id}>\n"
            "**👥 Target Roles:** None\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        preview_em = discord.Embed(title="🛠️ Announcement Builder", description=builder_desc, color=0x818CF8)
        
        builder_msg = await interaction.channel.send(embed=preview_em, view=view)
        view.builder_message = builder_msg

class AppendTextModal(discord.ui.Modal):
    def __init__(self, main_view, action_type, title, placeholder=""):
        super().__init__(title=title)
        self.main_view = main_view
        self.action_type = action_type
        
        self.text_input = discord.ui.TextInput(
            label="Text to Append",
            style=discord.TextStyle.paragraph if action_type in ['quote', 'code', 'bullet', 'number'] else discord.TextStyle.short,
            placeholder=placeholder,
            required=True,
            max_length=2000
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        text = self.text_input.value
        appended_str = ""
        
        if self.action_type == "bold":
            appended_str = f"**{text}**"
        elif self.action_type == "italic":
            appended_str = f"*{text}*"
        elif self.action_type == "heading":
            appended_str = f"\n### {text}\n"
        elif self.action_type == "quote":
            lines = text.split('\n')
            appended_str = "\n" + "\n".join(f"> {line}" for line in lines) + "\n"
        elif self.action_type == "code":
            appended_str = f"\n```\n{text}\n```\n"
        elif self.action_type == "bullet":
            lines = text.split('\n')
            appended_str = "\n" + "\n".join(f"• {line}" for line in lines) + "\n"
        elif self.action_type == "number":
            lines = text.split('\n')
            appended_str = "\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines)) + "\n"

        # Apply using history block
        new_body = self.main_view.body_text + (" " if self.main_view.body_text and not self.main_view.body_text.endswith('\n') and not appended_str.startswith('\n') else "") + appended_str
        self.main_view.push_history(new_body)
        
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.main_view.refresh_ui()

class RawTextModal(discord.ui.Modal, title="Edit Raw Text"):
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        
        self.raw_text = discord.ui.TextInput(
            label="Raw Markdown Text",
            style=discord.TextStyle.paragraph,
            default=main_view.body_text,
            required=True,
            max_length=4000
        )
        self.add_item(self.raw_text)

    async def on_submit(self, interaction: discord.Interaction):
        self.main_view.push_history(self.raw_text.value)
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.main_view.refresh_ui()

class AnnouncementMediaModal(discord.ui.Modal, title="Attach Media URL"):
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        
        self.media_url = discord.ui.TextInput(
            label="Image / Video URL",
            style=discord.TextStyle.short,
            placeholder="https://example.com/image.png",
            required=False,
            default=self.main_view.media_url,
            max_length=500
        )
        self.add_item(self.media_url)

    async def on_submit(self, interaction: discord.Interaction):
        self.main_view.media_url = self.media_url.value
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.main_view.refresh_ui()

class AnnouncementTemplateModal(discord.ui.Modal, title="Save as Template"):
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        
        self.template_name = discord.ui.TextInput(
            label="Template Name",
            style=discord.TextStyle.short,
            placeholder="e.g. event_update, warning",
            required=True,
            max_length=50
        )
        self.add_item(self.template_name)

    async def on_submit(self, interaction: discord.Interaction):
        save_announcement_template(self.template_name.value, self.main_view.title_text, self.main_view.body_text)
        await interaction.response.send_message(f"✅ Template `{self.template_name.value}` saved successfully!", ephemeral=True)

class AnnouncementScheduleModal(discord.ui.Modal, title="Schedule Announcement"):
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        
        self.time_input = discord.ui.TextInput(
            label="Schedule Time (HH:MM) [UK Time]",
            style=discord.TextStyle.short,
            placeholder="e.g. 18:00",
            required=True,
            max_length=5
        )
        self.add_item(self.time_input)

    async def on_submit(self, interaction: discord.Interaction):
        # We save this specifically on the view so the finalize button handles it.
        self.main_view.schedule_time_str = self.time_input.value
        if not interaction.response.is_done():
            await interaction.response.defer()
        await self.main_view.refresh_ui()

class AnnouncementTemplateBrowserView(discord.ui.View):
    def __init__(self, ctx, templates):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.templates = templates
        
        options = []
        for key in list(templates.keys())[:25]: # Discord max is 25
            options.append(discord.SelectOption(label=key, value=key, emoji="📝"))
            
        self.template_select = discord.ui.Select(
            custom_id="ann_template_select",
            placeholder="📂 Select a template to load...",
            options=options,
            min_values=1, max_values=1, row=0
        )
        self.template_select.callback = self.template_callback
        self.add_item(self.template_select)
        
    async def template_callback(self, interaction: discord.Interaction):
        selected_key = self.template_select.values[0]
        template_data = self.templates[selected_key]
        
        await interaction.response.defer()
        
        gif_url = get_bot_gif("ANNOUNCEMENT_GIF")
        embeds_list = []
        if gif_url:
            gif_em = discord.Embed(color=EMBED_COLOR)
            gif_em.set_image(url=gif_url)
            embeds_list.append(gif_em)

        em = discord.Embed(
            title=template_data["title"],
            description=template_data["body"],
            color=EMBED_COLOR,
            timestamp=datetime.now(UK_TZ)
        )
        em.set_footer(text=FOOTER_TEXT)
        embeds_list.append(em)
        
        msg = await interaction.channel.send(content="", embeds=embeds_list)
        view = AnnouncementBuilderView(self.ctx, msg, template_data["body"])
        view.title_text = template_data["title"]
        
        builder_desc = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"**📝 Channel:** <#{view.target_channel_id}>\n"
            "**🔔 Pings:** None\n"
            "**🖼️ Media:** None\n"
            "**⏰ Schedule:** Send Now\n"
            "**🏷️ Reactions:** No\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        preview_em = discord.Embed(title="🛠️ Advanced Announcement Builder", description=builder_desc, color=0x818CF8)
        
        builder_msg = await interaction.channel.send(embed=preview_em, view=view)
        view.builder_message = builder_msg
        
        # Stop the old dashboard view
        self.stop()
        try:
            await interaction.message.delete()
        except:
            pass

class AnnouncementDashboardView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=300)
        self.ctx = ctx
        
    @discord.ui.button(label="📢 Create Announcement", style=discord.ButtonStyle.primary, row=0)
    async def btn_create(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Not your session!", ephemeral=True)
            return
        await interaction.response.send_modal(AnnouncementCreateModal(self.ctx))
        self.stop()
        try:
            await interaction.message.delete()
        except:
            pass
        
    @discord.ui.button(label="📁 View Templates", style=discord.ButtonStyle.secondary, row=0)
    async def btn_templates(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return
            
        templates = load_announcement_templates()
        if not templates:
            await interaction.response.send_message("⚠️ No templates have been saved yet!", ephemeral=True)
            return
            
        em = discord.Embed(
            title="📂 Announcement Templates",
            description="Select a template from the dropdown below to load it into the builder.",
            color=0x4F46E5
        )
        await interaction.response.send_message(embed=em, view=AnnouncementTemplateBrowserView(self.ctx, templates), ephemeral=True)



@bot.command(name="announcement")
@commands.has_permissions(administrator=True)
async def announcement_cmd(ctx):
    """Open the Advanced Announcement Dashboard."""
    em = discord.Embed(
        title="📢 Announcement Control Panel",
        description=("Welcome to the Advanced Announcement System.\n\n"
                     "Click **Create Announcement** to draft a new message, or manage templates below."),
        color=0x4F46E5,
        timestamp=datetime.now(UK_TZ)
    )
    em.set_footer(text=FOOTER_TEXT)
    await ctx.reply(embed=em, view=AnnouncementDashboardView(ctx))


# ---------- !leaderboard ----------
@bot.command(name="leaderboard")
async def leaderboard_cmd(ctx):
    if not all_time_leaderboard:
        em = make_embed(
            title="🏆  Leaderboard",
            description="No data yet! Participate in a session to get on the board.",
            color=EMBED_COLOR_WARN,
        )
        await ctx.reply(embed=em, mention_author=False)
        return

    top    = all_time_leaderboard.most_common(10)
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines  = [f"{medals.get(r, f'**#{r}**')} <@{uid}> — **{count}** session(s)"
              for r, (uid, count) in enumerate(top, 1)]

    em = make_embed(
        title="🏆  All-Time Leaderboard",
        description="\n".join(lines),
        color=EMBED_COLOR,
    )
    await ctx.reply(embed=em, mention_author=False)
# ---------- !quote ----------
@bot.command(name="quote")
async def quote_cmd(ctx):
    # Try fetching from API Ninjas
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"X-Api-Key": QUOTES_API_KEY}
            async with session.get("https://api.api-ninjas.com/v1/quotes", headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        text = data[0]["quote"]
                        author = data[0]["author"]
                    else:
                        raise ValueError("Empty response")
                else:
                    raise ValueError(f"API returned {resp.status}")
    except Exception:
        # Fallback to hardcoded quotes
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
    if isinstance(error, CommandNotFound):
        wrong_cmd = ctx.message.content.split()[0]
        em = make_embed(
            title="❌  Unknown Command!",
            description=(
                f"`{wrong_cmd}` is not recognized.\n\n"
                "**Try these:**\n"
                "> `!help` — Interactive command menu\n"
                "> `!events` — Event schedule\n"
                "> `!status` — Active sessions"
            ),
            color=EMBED_COLOR_CLOSE,
        )
        await ctx.reply(embed=em, mention_author=False, delete_after=15)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply(
            "❌ You don't have permission to use this command.",
            delete_after=8, mention_author=False
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(
            f"❌ Missing argument: `{error.param.name}` — use `!help` for usage.",
            delete_after=10, mention_author=False
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.reply(
            "❌ Invalid argument provided. Use `!help` for usage.",
            delete_after=10, mention_author=False
        )
    else:
        # Log all other errors but don't re-raise — prevents bot crash
        print(f"[CMD ERROR] Command '{ctx.command}' raised: {type(error).__name__}: {error}")


# =========================
# 🚀 WHEN BOT STARTS
# =========================

@bot.event
async def on_ready():
    global bot_start_time
    bot_start_time = datetime.now(UK_TZ)
    print(f"✅ Bot is ready! Logged in as {bot.user}")
    configured = {k: v for k, v in CHANNEL_IDS.items() if v != 0}
    print(f"📡 Configured channels: {configured}")

    # ── Load cogs (modular extensions) ──────────────────────────
    try:
        await bot.load_extension("cogs.ban_manager")
        print("🔨 Ban Manager cog loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Ban Manager cog: {e}")

    try:
        await bot.load_extension("cogs.command_center")
        print("✦ Command Center cog loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Command Center cog: {e}")

    try:
        await bot.load_extension("cogs.deep_clean")
        print("🧹 Deep Clean cog loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Deep Clean cog: {e}")

    try:
        await bot.load_extension("cogs.clean_panel")
        print("🧹 Clean Panel cog loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Clean Panel cog: {e}")


    # ── Start background tasks ──────────────────────────────────
    event_scheduler.start()
    print("🔁 UK Event scheduler started")
    auto_clean_channels.start()
    print("🧹 24-hour auto-clean started")

    # ── Start Dashboard Web Server ──────────────────────────────
    from dashboard.server import create_dashboard
    dashboard_thread = threading.Thread(
        target=create_dashboard,
        args=(bot, active_sessions, all_time_leaderboard, bot_start_time),
        daemon=True,
        name="DashboardThread"
    )
    dashboard_thread.start()
    port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', 5000)))
    print(f"🌐 SARKAR Dashboard Link: http://51.68.34.78:{port}/?fresh=1")


# =========================
# 🔑 START BOT
# =========================

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_TOKEN not found in .env file!")
    bot.run(token)
