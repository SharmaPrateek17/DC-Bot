from flask import Flask, session, redirect, url_for, request, jsonify, render_template, send_from_directory
from functools import wraps
import os, json, asyncio, requests
from datetime import datetime
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

import pytz

# ── import auth helpers ──────────────────────────────────────
from dashboard.auth import create_user, verify_user, update_user, change_password, get_user, load_users

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET', 'antigravity-super-secret-key-change-me')

UK_TZ = pytz.timezone("Europe/London")

# ── Shared bot references (set by create_dashboard) ──────────
_bot           = None
_sessions      = None
_leaderboard   = None
_bot_start_time = None

# ── Bot event channel IDs (imported from Bot.py context) ─────
CHANNEL_IDS_MAP = {
    "INFORMAL":      1473346234763706549,
    "STATE_CONTROL": 1475815532631560359,
    "BIZ_WAR":       1475816139358732371,
    "RP_TICKET":     1475816007900725298,
    "OTHER_EVENTS":  1476228818917392424,
}
PAGER_CHANNEL_ID         = 1476312468140724267
FAMILY_ROLE_ID           = 1467869393282138405
SPECIAL_EVENT_CHANNEL_ID = 1480059758831603804

ANNOUNCEMENT_CHANNELS = {
    "Announcement Section": 1476284162737700915,
    "Fam Announcement":     1476284338889822208,
    "Turf Announcement":    1467862732786110699,
}

# ── Event lists (same as Bot.py) ─────────────────────────────
EVENT_LIST_DATA = [
    ("Every :30", "🎉 Informal 🎉", "INFORMAL", 10, "Daily"),
    ("01:05",     "💼 Business War 💼", "BIZ_WAR", 25, "Daily"),
    ("19:05",     "💼 Business War 💼", "BIZ_WAR", 25, "Daily"),
    ("16:00",     "🏛️ State Control 🏛️", "STATE_CONTROL", 10, "Daily"),
    ("10:30",     "🎫 Factory of RP Tickets 🎫", "RP_TICKET", 25, "Daily"),
    ("16:30",     "🎫 Factory of RP Tickets 🎫", "RP_TICKET", 25, "Daily"),
    ("22:30",     "🎫 Factory of RP Tickets 🎫", "RP_TICKET", 25, "Daily"),
    ("00:00",     "🌿 Weed Farm 🌿", "OTHER_EVENTS", 25, "Daily"),
    ("01:10",     "⚓ Harbor ⚓", "OTHER_EVENTS", 25, "Daily"),
    ("02:20",     "🏨 Hotel Takeover 🏨", "OTHER_EVENTS", 25, "Daily"),
    ("03:20",     "🔫 Weapons Factory 🔫", "OTHER_EVENTS", 25, "Daily"),
    ("04:10",     "⚓ Harbor ⚓", "OTHER_EVENTS", 25, "Daily"),
    ("06:00",     "🌿 Weed Farm 🌿", "OTHER_EVENTS", 25, "Daily"),
    ("07:10",     "⚓ Harbor ⚓", "OTHER_EVENTS", 25, "Daily"),
    ("08:00",     "🌿 Weed Farm 🌿", "OTHER_EVENTS", 25, "Daily"),
    ("10:00",     "🌿 Weed Farm 🌿", "OTHER_EVENTS", 25, "Daily"),
    ("10:10",     "⚓ Harbor ⚓", "OTHER_EVENTS", 25, "Daily"),
    ("10:20",     "🔫 Weapons Factory 🔫", "OTHER_EVENTS", 25, "Daily"),
    ("12:00",     "🌿 Weed Farm 🌿", "OTHER_EVENTS", 25, "Daily"),
    ("13:10",     "⚓ Harbor ⚓", "OTHER_EVENTS", 25, "Daily"),
    ("14:00",     "🌿 Weed Farm 🌿", "OTHER_EVENTS", 25, "Daily"),
    ("14:20",     "🔥 Foundry 🔥", "OTHER_EVENTS", 25, "Daily"),
    ("16:00",     "🌿 Weed Farm 🌿", "OTHER_EVENTS", 25, "Daily"),
    ("16:10",     "⚓ Harbor ⚓", "OTHER_EVENTS", 25, "Daily"),
    ("22:20",     "🔫 Weapons Factory 🔫", "OTHER_EVENTS", 25, "Daily"),
]

SPECIAL_EVENT_DATA = [
    ("17:15", "🏬 Mall 🏬", 5, "Daily"),
    ("17:30", "🏦 Bank Robbery 🏦", 25, "Mon/Wed/Sat"),
    ("20:20", "🔓 Prison Protection 🔓", 25, "Friday"),
    ("10:00", "🧪 Drug Lab 🧪", 25, "Daily"),
]

PAGER_MESSAGES = {
    "Serious": [
        "All family members are requested to come to the city and prepare for upcoming events. Active participation will be rewarded.",
        "⚠️ Family Notice: Events are starting soon. All members should report to the city and be ready for participation."
    ],
    "Motivational": [
        "🔥 Fam Call: Events are about to begin! Come to the city, show your skills, and earn extra bonuses.",
        "💪 Family Power: Strong families move together. Join the events in the city and help us dominate."
    ],
    "Funny": [
        "😂 Fam Pager: If you're sleeping wake up. If you're eating finish fast. Events are starting!",
        "🤣 Friendly Reminder: The city is calling. Your bonus might get stolen if you stay offline."
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

# ── Auth guard ───────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'username' not in session:
        return {}
    return get_user(session['username'])

def run_coro(coro):
    """Run a coroutine on the bot's event loop from a Flask thread."""
    if _bot and _bot.loop:
        future = asyncio.run_coroutine_threadsafe(coro, _bot.loop)
        try:
            return future.result(timeout=5)
        except Exception as e:
            print(f"[Dashboard] Coro error: {e}")
    return None

# ── Static files ─────────────────────────────────────────────
@app.route('/avatars/<filename>')
def serve_avatar(filename):
    avatars_dir = os.path.join(os.path.dirname(__file__), 'avatars')
    return send_from_directory(avatars_dir, filename)

# ════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ════════════════════════════════════════════════════════════

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

@app.route('/login', methods=['GET'])
def login_page():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login/discord', methods=['GET'])
def login_discord():
    client_id = os.getenv('DISCORD_CLIENT_ID')
    if not client_id:
        return "DISCORD_CLIENT_ID not found in .env file. Please follow the instructions in the implementation plan to add it.", 500
    
    redirect_uri = request.url_root.rstrip('/') + url_for('callback_discord')
    url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    return redirect(url)

@app.route('/callback/discord', methods=['GET'])
def callback_discord():
    client_id = os.getenv('DISCORD_CLIENT_ID')
    client_secret = os.getenv('DISCORD_CLIENT_SECRET')
    if not client_id or not client_secret:
        return "Discord API keys missing in .env", 500
        
    code = request.args.get('code')
    if not code:
        return "Discord authentication failed or was cancelled.", 400
        
    redirect_uri = request.url_root.rstrip('/') + url_for('callback_discord')
    
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    if not r.ok:
        return f"Failed to get token from Discord: {r.text}", 400
        
    token = r.json().get('access_token')
    
    # Get user profile
    r_user = requests.get("https://discord.com/api/users/@me", headers={'Authorization': f'Bearer {token}'})
    if not r_user.ok:
        return "Failed to fetch Discord user profile.", 400
        
    user_data = r_user.json()
    discord_id = user_data.get('id')
    username = str(user_data.get('username'))
    avatar = user_data.get('avatar')
    avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.png" if avatar else ""
    discord_tag = f"{username}#0000" if user_data.get('discriminator') == '0' else f"{username}#{user_data.get('discriminator', '0000')}"
    
    users = load_users()
    if username not in users:
        # Create a new user automatically
        from dashboard.auth import _hash_password
        users[username] = {
            "password": _hash_password("discord_auth_no_pass_needed"),
            "role": "Member",
            "first_name": username,
            "last_name": "",
            "discord_tag": discord_tag,
            "email": "",
            "avatar_emoji": "😎",
            "avatar_photo": avatar_url
        }
    else:
        # Update existing user's discord details
        users[username]['avatar_photo'] = avatar_url
        users[username]['discord_tag'] = discord_tag
        
    # Save directly to bypass the basic create_user logic which requires manual inputs
    with open('dashboard/users.json', 'w') as f:
        json.dump(users, f, indent=4)
        
    session['username'] = username
    return redirect(url_for('home'))

@app.route('/api/login', methods=['POST'])
def api_login():
    d = request.get_json()
    ok, result = verify_user(d.get('username', ''), d.get('password', ''))
    if ok:
        session['username'] = d['username']
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': result}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    d = request.get_json()
    ok, msg = create_user(
        username = d.get('username', ''),
        password = d.get('password', ''),
        first    = d.get('first_name', ''),
        last     = d.get('last_name', ''),
        email    = d.get('email', ''),
        discord  = d.get('discord_tag', ''),
        avatar   = d.get('avatar_emoji', '😎'),
    )
    if ok:
        session['username'] = d['username']
    return jsonify({'ok': ok, 'message': msg})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/')
def landing_page():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def home():
    return render_template('home.html', user=get_current_user(), active='home')

@app.route('/sessions')
@login_required
def sessions_page():
    return render_template('sessions.html', user=get_current_user(), active='sessions')

@app.route('/schedule')
@login_required
def schedule_page():
    return render_template('schedule.html', user=get_current_user(), active='schedule',
                           events=EVENT_LIST_DATA, specials=SPECIAL_EVENT_DATA)

@app.route('/pager')
@login_required
def pager_page():
    return render_template('pager.html', user=get_current_user(), active='pager',
                           pager_messages=PAGER_MESSAGES)

@app.route('/announce')
@login_required
def announce_page():
    return render_template('announce.html', user=get_current_user(), active='announce',
                           channels=ANNOUNCEMENT_CHANNELS)

@app.route('/moderation')
@login_required
def moderation_page():
    return render_template('moderation.html', user=get_current_user(), active='moderation',
                           channels=CHANNEL_IDS_MAP)

@app.route('/leaderboard')
@login_required
def leaderboard_page():
    return render_template('leaderboard.html', user=get_current_user(), active='leaderboard')

@app.route('/gifs')
@login_required
def gifs_page():
    return render_template('gifs.html', user=get_current_user(), active='gifs')

@app.route('/quick')
@login_required
def quick_page():
    return render_template('quick.html', user=get_current_user(), active='quick')

@app.route('/manager')
@login_required
def manager_page():
    return render_template('manager.html', user=get_current_user(), active='manager',
                           events=EVENT_LIST_DATA, specials=SPECIAL_EVENT_DATA,
                           channels=CHANNEL_IDS_MAP)

@app.route('/about')
@login_required
def about_page():
    session_count = len(_sessions) if _sessions else 0
    return render_template('about.html', user=get_current_user(), active='about',
                           session_count=session_count)

@app.route('/owner')
@login_required
def owner_page():
    return render_template('owner.html', user=get_current_user(), active='owner')

@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', user=get_current_user(), active='profile')

# ════════════════════════════════════════════════════════════
#  DATA API ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/api/status')
@login_required
def api_status():
    uptime_str = 'Starting...'
    if _bot_start_time:
        delta = datetime.now(UK_TZ) - _bot_start_time
        h, rem = divmod(int(delta.total_seconds()), 3600)
        m = rem // 60
        uptime_str = f'{h}h {m}m' if h > 0 else f'{m}m'
    return jsonify({
        'bot_name':      str(_bot.user) if _bot else 'Offline',
        'session_count': len(_sessions) if _sessions else 0,
        'uk_time':       datetime.now(UK_TZ).strftime('%H:%M:%S'),
        'uptime':        uptime_str,
        'online':        _bot is not None and not _bot.is_closed(),
    })

@app.route('/api/sessions')
@login_required
def api_sessions():
    if not _sessions:
        return jsonify([])
    result = []
    for ch_id, sess in _sessions.items():
        ch = _bot.get_channel(ch_id) if _bot else None
        confirmed_names = []
        waiting_names   = []
        if ch and ch.guild:
            for uid in sess.get('confirmed', []):
                m = ch.guild.get_member(uid)
                confirmed_names.append(m.display_name if m else f'User#{uid}')
            for uid in sess.get('waiting_list', []):
                m = ch.guild.get_member(uid)
                waiting_names.append(m.display_name if m else f'User#{uid}')
        elapsed = ''
        closes_in = ''
        if sess.get('start_time'):
            delta = datetime.now(UK_TZ) - sess['start_time']
            secs  = int(delta.total_seconds())
            elapsed   = f"{secs//60}m {secs%60}s"
            left      = max(0, 480 - secs)
            closes_in = f"{left//60}m {left%60}s"
        result.append({
            'channel_id':      ch_id,
            'channel_name':    ch.name if ch else f'Channel {ch_id}',
            'event_name':      sess.get('event_name', ''),
            'confirmed':       confirmed_names,
            'waiting':         waiting_names,
            'confirmed_count': len(sess.get('confirmed', [])),
            'waiting_count':   len(sess.get('waiting_list', [])),
            'max_participants':sess.get('max_participants', 0),
            'elapsed':         elapsed,
            'closes_in':       closes_in,
        })
    return jsonify(result)

@app.route('/api/leaderboard')
@login_required
def api_leaderboard():
    if not _leaderboard:
        return jsonify([])
    top    = _leaderboard.most_common(10)
    guild  = _bot.guilds[0] if _bot and _bot.guilds else None
    result = []
    for rank, (uid, count) in enumerate(top, 1):
        member = guild.get_member(uid) if guild else None
        result.append({
            'rank':  rank,
            'name':  member.display_name if member else f'User#{uid}',
            'count': count,
        })
    return jsonify(result)

@app.route('/api/gifs', methods=['GET'])
@login_required
def api_gifs_get():
    path = 'config/eventGifs.json'
    if not os.path.exists(path):
        return jsonify({})
    with open(path, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/api/gifs', methods=['POST'])
@login_required
def api_gifs_save():
    path = 'config/eventGifs.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(request.json, f, indent=4)
    return jsonify({'ok': True})

@app.route('/api/botgifs', methods=['GET'])
@login_required
def api_botgifs_get():
    path = 'config/botGifs.json'
    if not os.path.exists(path):
        return jsonify({})
    with open(path, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/api/botgifs', methods=['POST'])
@login_required
def api_botgifs_save():
    path = 'config/botGifs.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(request.json, f, indent=4)
    return jsonify({'ok': True})

@app.route('/api/templates', methods=['GET'])
@login_required
def api_templates_get():
    path = 'config/annTemplates.json'
    if not os.path.exists(path):
        return jsonify({})
    with open(path, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/api/landing_stats', methods=['GET'])
def api_landing_stats():
    guild = _bot.guilds[0] if _bot and _bot.guilds else None
    active_events = len(_sessions) if _sessions else 0
    member_count = guild.member_count if guild else 247000
    
    resp = jsonify({
        'members': f"{member_count:,}",
        'messages': "1.2M",
        'events': f"{active_events}",
        'prize_pool': "$50K"
    })
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp

# ════════════════════════════════════════════════════════════
#  BOT ACTION ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/api/close_session', methods=['POST'])
@login_required
def api_close_session():
    from Bot import close_session
    ch_id = int(request.json.get('channel_id', 0))
    run_coro(close_session(ch_id))
    return jsonify({'ok': True})

@app.route('/api/start_session', methods=['POST'])
@login_required
def api_start_session():
    from Bot import open_session
    d = request.json
    run_coro(open_session(
        target_channel_id  = int(d['channel_id']),
        event_name         = d['event_name'],
        max_participants   = int(d['max_participants']),
        custom_timer_seconds = int(d.get('timer_seconds', 480)),
    ))
    return jsonify({'ok': True})

@app.route('/api/send_pager', methods=['POST'])
@login_required
def api_send_pager():
    import discord
    d    = request.json
    text = d.get('message', '')
    async def _send():
        ch = _bot.get_channel(PAGER_CHANNEL_ID)
        if ch:
            em = discord.Embed(
                title="📟 Pager Message",
                description=f"<@&{FAMILY_ROLE_ID}>\n\n**{text}**",
                color=0xF59E0B,
            )
            await ch.send(embed=em)
    run_coro(_send())
    return jsonify({'ok': True})

@app.route('/api/announce', methods=['POST'])
@login_required
def api_announce():
    import discord
    d      = request.json
    ch_id  = int(d.get('channel_id', 0))
    title  = d.get('title', 'ANNOUNCEMENT')
    body   = d.get('body', '')
    async def _send():
        ch = _bot.get_channel(ch_id)
        if ch:
            em = discord.Embed(title=title, description=body, color=0x7C3AED)
            em.set_footer(text="Event Automation Manager ✦")
            await ch.send(embed=em)
    run_coro(_send())
    return jsonify({'ok': True})

@app.route('/api/raid', methods=['POST'])
@login_required
def api_raid():
    import discord
    async def _send():
        ch = _bot.get_channel(CHANNEL_IDS_MAP.get('OTHER_EVENTS', 0))
        if ch:
            em = discord.Embed(
                title="🚨 FAMILY RAID 🚨",
                description="**EVERYONE COME — WE ARE ON RAID** 🚨\n\nDrop everything and get in NOW!",
                color=0xEF4444,
            )
            await ch.send(embed=em)
    run_coro(_send())
    return jsonify({'ok': True})

@app.route('/api/robbery', methods=['POST'])
@login_required
def api_robbery():
    from Bot import open_session
    ch_id = CHANNEL_IDS_MAP.get('OTHER_EVENTS', 0)
    run_coro(open_session(ch_id, "Store Robbery", 25))
    return jsonify({'ok': True})

@app.route('/api/purge', methods=['POST'])
@login_required
def api_purge():
    d     = request.json
    ch_id = int(d.get('channel_id', 0))
    limit = min(int(d.get('limit', 100)), 500)
    async def _purge():
        ch = _bot.get_channel(ch_id)
        if ch:
            await ch.purge(limit=limit)
    run_coro(_purge())
    return jsonify({'ok': True})

# ════════════════════════════════════════════════════════════
#  PROFILE API ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update():
    data = request.get_json()
    update_user(session['username'], data)
    return jsonify({'ok': True})

@app.route('/api/profile/change-password', methods=['POST'])
@login_required
def api_change_password():
    d = request.get_json()
    ok, msg = change_password(session['username'], d.get('current', ''), d.get('new', ''))
    return jsonify({'ok': ok, 'message': msg})

@app.route('/api/profile/upload-avatar', methods=['POST'])
@login_required
def api_upload_avatar():
    f = request.files.get('avatar')
    if f and f.filename:
        ext      = f.filename.rsplit('.', 1)[-1].lower()
        if ext not in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
            return jsonify({'ok': False, 'error': 'Invalid file type'})
        filename = f"{session['username']}_avatar.{ext}"
        avatars_dir = os.path.join(os.path.dirname(__file__), 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        f.save(os.path.join(avatars_dir, filename))
        update_user(session['username'], {'avatar_photo': f'/avatars/{filename}'})
        return jsonify({'ok': True, 'path': f'/avatars/{filename}'})
    return jsonify({'ok': False, 'error': 'No file received'})

@app.route('/api/me')
@login_required
def api_me():
    return jsonify(get_current_user())

# ════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════

def create_dashboard(bot, sessions, leaderboard, bot_start_time=None):
    global _bot, _sessions, _leaderboard, _bot_start_time
    _bot            = bot
    _sessions       = sessions
    _leaderboard    = leaderboard
    _bot_start_time = bot_start_time
    port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', 5000)))
    print("================================================================")
    print("🚀 SARKAR DASHBOARD IS LIVE ON KATABUMP!")
    print("================================================================")
    print(f"   CLICK HERE TO OPEN YOUR DASHBOARD:")
    print(f"   http://51.68.34.78:{port}/?fresh=1")
    print("================================================================")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
