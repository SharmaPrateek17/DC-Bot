import paramiko
import os
import time

host = "sftp.fr-node-60.katabump.com"
port = 2022
username = "304a797143d5c79.9288f1a3"
password = "2cec2ab0da7e"

print(f"🔄 Connecting to Katabump SFTP ({host}:{port})...")
try:
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print("✅ Connected to Katabump Servers!")

    local_path = "c:/Terrible/Discord/Bot.py"
    remote_path = "Bot.py"

    def print_progress(transferred, total):
        print(f"🔼 Uploading Bot.py: {transferred}/{total} bytes...", end="\r")

    print(f"📦 Preparing to upload Bot.py (Size: {os.path.getsize(local_path)} bytes)...")
    sftp.put(local_path, remote_path, callback=print_progress)
    print("\n✅ Bot.py upload complete!")

    # Also upload requirements.txt (wavelink removed)
    req_local = "c:/Terrible/Discord/requirements.txt"
    req_remote = "requirements.txt"
    print(f"📦 Uploading requirements.txt ({os.path.getsize(req_local)} bytes)...")
    sftp.put(req_local, req_remote)
    print("✅ requirements.txt upload complete!")

    # Upload eventGifs config
    try:
        sftp.mkdir("config")
    except IOError:
        pass # Directory likely exists
    config_local = "c:/Terrible/Discord/config/eventGifs.json"
    config_remote = "config/eventGifs.json"
    print(f"📦 Uploading eventGifs.json ({os.path.getsize(config_local)} bytes)...")
    sftp.put(config_local, config_remote)
    print("✅ eventGifs.json upload complete!")

    # Upload botGifs config
    bot_config_local = "c:/Terrible/Discord/config/botGifs.json"
    bot_config_remote = "config/botGifs.json"
    if os.path.exists(bot_config_local):
        print(f"📦 Uploading botGifs.json ({os.path.getsize(bot_config_local)} bytes)...")
        sftp.put(bot_config_local, bot_config_remote)
        print("✅ botGifs.json upload complete!")

    # Upload annTemplates config
    ann_config_local = "c:/Terrible/Discord/config/annTemplates.json"
    ann_config_remote = "config/annTemplates.json"
    if os.path.exists(ann_config_local):
        print(f"📦 Uploading annTemplates.json ({os.path.getsize(ann_config_local)} bytes)...")
        sftp.put(ann_config_local, ann_config_remote)
        print("✅ annTemplates.json upload complete!")

    # Upload cogs (ban management system)
    try:
        sftp.mkdir("cogs")
    except IOError:
        pass  # Directory likely exists
    
    cog_init_local = "c:/Terrible/Discord/cogs/__init__.py"
    cog_init_remote = "cogs/__init__.py"
    if os.path.exists(cog_init_local):
        print(f"📦 Uploading cogs/__init__.py ({os.path.getsize(cog_init_local)} bytes)...")
        sftp.put(cog_init_local, cog_init_remote)
        print("✅ cogs/__init__.py upload complete!")

    ban_cog_local = "c:/Terrible/Discord/cogs/ban_manager.py"
    ban_cog_remote = "cogs/ban_manager.py"
    if os.path.exists(ban_cog_local):
        print(f"📦 Uploading cogs/ban_manager.py ({os.path.getsize(ban_cog_local)} bytes)...")
        sftp.put(ban_cog_local, ban_cog_remote)
        print("✅ cogs/ban_manager.py upload complete!")

    cc_cog_local = "c:/Terrible/Discord/cogs/command_center.py"
    cc_cog_remote = "cogs/command_center.py"
    if os.path.exists(cc_cog_local):
        print(f"📦 Uploading cogs/command_center.py ({os.path.getsize(cc_cog_local)} bytes)...")
        sftp.put(cc_cog_local, cc_cog_remote)
        print("✅ cogs/command_center.py upload complete!")

    dc_cog_local = "c:/Terrible/Discord/cogs/deep_clean.py"
    dc_cog_remote = "cogs/deep_clean.py"
    if os.path.exists(dc_cog_local):
        print(f"📦 Uploading cogs/deep_clean.py ({os.path.getsize(dc_cog_local)} bytes)...")
        sftp.put(dc_cog_local, dc_cog_remote)
        print("✅ cogs/deep_clean.py upload complete!")

    cp_cog_local = "c:/Terrible/Discord/cogs/clean_panel.py"
    cp_cog_remote = "cogs/clean_panel.py"
    if os.path.exists(cp_cog_local):
        print(f"📦 Uploading cogs/clean_panel.py ({os.path.getsize(cp_cog_local)} bytes)...")
        sftp.put(cp_cog_local, cp_cog_remote)
        print("✅ cogs/clean_panel.py upload complete!")

    # Upload dashboard folder (Flask web dashboard)
    dashboard_local = "c:/Terrible/Discord/dashboard"
    if os.path.exists(dashboard_local):
        print("📦 Uploading dashboard/ folder...")
        # Create dashboard directories
        for dir_name in ["dashboard", "dashboard/templates", "dashboard/avatars"]:
            try:
                sftp.mkdir(dir_name)
            except IOError:
                pass  # Directory likely exists

        # Upload dashboard Python files
        for fname in ["__init__.py", "server.py", "auth.py"]:
            local_f = os.path.join(dashboard_local, fname)
            if os.path.exists(local_f):
                print(f"  📦 Uploading dashboard/{fname} ({os.path.getsize(local_f)} bytes)...")
                sftp.put(local_f, f"dashboard/{fname}")
                print(f"  ✅ dashboard/{fname} upload complete!")

        # Upload all templates
        templates_dir = os.path.join(dashboard_local, "templates")
        if os.path.exists(templates_dir):
            for fname in os.listdir(templates_dir):
                if fname.endswith(".html"):
                    local_f = os.path.join(templates_dir, fname)
                    print(f"  📦 Uploading dashboard/templates/{fname} ({os.path.getsize(local_f)} bytes)...")
                    sftp.put(local_f, f"dashboard/templates/{fname}")
                    print(f"  ✅ dashboard/templates/{fname} upload complete!")
        print("✅ Dashboard folder upload complete!")

    print("🔍 Verifying remote Bot.py file size...")
    stat = sftp.stat(remote_path)
    print(f"📄 Remote Bot.py Size: {stat.st_size} bytes - Modified: {time.ctime(stat.st_mtime)}")
    print("✨ Remote code successfully updated!")

except Exception as e:
    print(f"\n❌ Error during upload: {e}")
finally:
    try:
        sftp.close()
        transport.close()
    except:
        pass

print("\n🚀 Please restart your Katabump server from the dashboard to apply the changes!")
