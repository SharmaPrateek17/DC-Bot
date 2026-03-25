import json, os
from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def create_user(username, password, first='', last='', email='', discord='', avatar='😎'):
    users = load_users()
    if username.lower() in {k.lower() for k in users}:
        return False, 'Username already taken'
    if len(password) < 6:
        return False, 'Password must be at least 6 characters'
    users[username] = {
        'password_hash': generate_password_hash(password),
        'first_name':    first,
        'last_name':     last,
        'email':         email,
        'discord_tag':   discord,
        'avatar_emoji':  avatar,
        'avatar_photo':  None,
        'bio':           '',
        'role':          'Owner',
        'location':      '',
        'timezone':      'Europe/London',
    }
    save_users(users)
    return True, 'Account created!'

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return False, 'Username not found'
    if not check_password_hash(users[username]['password_hash'], password):
        return False, 'Incorrect password'
    return True, users[username]

def update_user(username, data: dict):
    users = load_users()
    if username in users:
        data.pop('password_hash', None)
        users[username].update(data)
        save_users(users)
        return True
    return False

def change_password(username, current_pw, new_pw):
    users = load_users()
    if username not in users:
        return False, 'User not found'
    if not check_password_hash(users[username]['password_hash'], current_pw):
        return False, 'Current password is wrong'
    if len(new_pw) < 6:
        return False, 'New password too short'
    users[username]['password_hash'] = generate_password_hash(new_pw)
    save_users(users)
    return True, 'Password updated!'

def get_user(username):
    users = load_users()
    return users.get(username, {})
