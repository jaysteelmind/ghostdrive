import os
import subprocess
import platform

# Define each game with exact path + launcher filename
games = {
    "tuxemon": {
        "path": os.path.join(os.path.dirname(__file__), "games", "tuxemon"),
        "launcher": "run_tuxemon.py"
    },
    "supertuxkart": {
        "path": os.path.join(os.path.dirname(__file__), "games", "SuperTuxKart"),
        "launcher": "supertuxkart.exe"
    },
    "pingus": {
        "path": os.path.join(os.path.dirname(__file__), "games", "pingus"),
        "launcher": "pingus.exe"
    },
    "singularity": {
        "path": os.path.join(os.path.dirname(__file__), "games", "singularity-100"),
        "launcher": "singularity_win.exe"
    },
    "xonotic": {
        "path": os.path.join(os.path.dirname(__file__), "games", "Xonotic"),
        "launcher": "xonotic.exe"
    },
}

def launch_game(game_name):
    game_name = game_name.lower()
    if game_name not in games:
        print(f"❌ Game '{game_name}' not found.")
        return

    entry = games[game_name]
    path = entry["path"]
    launcher = entry["launcher"]
    launcher_path = os.path.join(path, launcher)

    if not os.path.exists(path):
        print(f"❌ Game path for '{game_name}' does not exist.")
        return

    if not os.path.exists(launcher_path):
        print(f"❌ Launcher '{launcher}' not found in {path}.")
        return

    print(f"\n🎮 Launching {game_name}...")

    system = platform.system()

    if system == "Windows":
        if launcher.endswith(".exe"):
            subprocess.Popen(f'start "" "{launcher_path}" -basedir "{path}"', shell=True)
        elif launcher.endswith(".py"):
            subprocess.Popen(["py", "-3", launcher], cwd=path)
        else:
            print(f"⚠️ Unsupported launcher format: {launcher}")

    elif system == "Linux" or system == "Darwin":
        subprocess.Popen(["chmod", "+x", launcher_path])
        subprocess.Popen([launcher_path], cwd=path)

    else:
        print("❌ Unsupported OS.")
