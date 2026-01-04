# jynx_operator_ui.py
# Refactored for UI integration – all outputs returned as strings, no input() or print()

import os
import subprocess
import socket
import getpass
import datetime
import psutil
import webbrowser
from cryptography.fernet import Fernet


def blackout_mode():
    try:
        disconnect_wifi()
        return "Blackout protocol activated — Wi-Fi disconnected."
    except Exception as e:
        return f"[ERROR] Blackout failed: {e}"



def disconnect_wifi():
    """
    Disconnects from the current Wi-Fi network using nmcli.
    Returns a message string describing the outcome.
    """
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
            capture_output=True, text=True
        )
        wifi_device = None
        for line in result.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 3 and parts[1] == "wifi" and parts[2] == "connected":
                wifi_device = parts[0]
                break

        if not wifi_device:
            return "[INFO] No active Wi-Fi connection found."

        result = subprocess.run(
            ["nmcli", "device", "disconnect", wifi_device],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return "[WIFI] Disconnected from current Wi-Fi network."
        return f"[WARNING] Disconnect attempt returned: {result.stdout} {result.stderr}"
    except Exception as e:
        return f"[ERROR] Failed to disconnect Wi-Fi: {e}"

def reconnect_wifi():
    """
    Tries to reconnect to any known WiFi network with saved credentials.
    Returns a message string describing the outcome.
    """
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
            capture_output=True, text=True
        )

        profiles = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 2 and parts[1] == "802-11-wireless":
                profiles.append(parts[0])

        if not profiles:
            return "[WARNING] No known WiFi networks found on this system."

        for ssid in profiles:
            result = subprocess.run(
                ["nmcli", "connection", "up", ssid],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return f"[SUCCESS] Successfully connected to known network: {ssid}"

        return "[ERROR] No known networks could be connected to at this time."

    except Exception as e:
        return f"[ERROR] Reconnection failed due to error: {e}"

def scan_networks():
    """
    Scans for available Wi-Fi networks using nmcli.
    Returns a formatted list of networks or an error message.
    """
    try:
        subprocess.run(
            ["nmcli", "device", "wifi", "rescan"],
            capture_output=True, text=True,
            timeout=10
        )
        result = subprocess.run(
            ["nmcli", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            return result.stdout
        return "[INFO] No networks found."
    except subprocess.TimeoutExpired:
        return "[WARNING] Network scan timed out."
    except Exception as e:
        return f"[ERROR] Failed to scan networks: {e}"

def activate_big_brother():
    try:
        webbrowser.open("https://chat.openai.com")
        return "Big Brother activated (browser opened)."
    except Exception as e:
        return f"[ERROR] Failed to activate Big Brother: {e}"


def status_report():
    try:
        # Get system uptime
        uptime_sec = int(psutil.boot_time())
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(uptime_sec)

        # Check battery (handles desktops)
        battery = psutil.sensors_battery()
        if battery:
            battery_status = f"{battery.percent}% {'(plugged in)' if battery.power_plugged else '(on battery)'}"
        else:
            battery_status = "N/A (no battery detected)"

        # Other system info
        ip = socket.gethostbyname(socket.gethostname())
        user = getpass.getuser()

        report = (
            "[NET] System Status:\n\n"
            f"- Uptime: {str(uptime).split('.')[0]}\n"
            f"- Battery: {battery_status}\n"
            f"- IP Address: {ip}\n"
            f"- Active User: {user}"
        )

        return report

    except Exception as e:
        return f"[ERROR] Status report unavailable: {e}"


def get_random_prompt():
    import os, random
    prompt_file = os.path.join(os.path.dirname(__file__), "soul_prompts.txt")
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
        return random.choice(prompts)
    except Exception:
        return "What do I need to let go of today?"


def soul_vent(filename=None, entry=None, passphrase=None, chosen_prompt=None):
    """
    UI-integrated Soul Vent protocol.
    Appends prompt + journal entry to a file, then encrypts it.
    Only includes the 'Thought Primer' and 'Begin Transmission' lines
    if the prompt is actually used.
    """
    import platform, datetime, os
    from filecrypt import get_fernet, encrypt_file

    messages = []
    if not chosen_prompt:
        chosen_prompt = "What do I need to let go of today?"

    journal_dir = os.path.join(os.path.dirname(__file__), "journal")
    os.makedirs(journal_dir, exist_ok=True)

    if filename:
        filename = f"{filename}.txt" if not filename.endswith(".txt") else filename
    else:
        timestamp = datetime.datetime.now().strftime("%d%b%Y_%I%M%p")
        filename = f"{timestamp}.txt"

    file_path = os.path.join(journal_dir, filename)

    # [EDIT] Write content — only include headers if prompt still present
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            cleaned_entry = entry.strip()

            # If the user kept the prompt (or modified it slightly), include it
            if chosen_prompt.strip() in cleaned_entry:
                f.write(f"{chosen_prompt.strip()}\n\n")

            # Write the main journal text
            f.write(cleaned_entry + "\n")

    except Exception as e:
        return f"[ERROR] Failed to write journal file: {e}"

    # [LOCK] Encrypt
    try:
        if passphrase:
            fernet = get_fernet(passphrase)
            encrypt_file(file_path, fernet)
        else:
            return "[WARNING] No passphrase provided — file left unencrypted."
    except Exception as e:
        return f"[ERROR] Encryption failed: {e}"

    return "[SUCCESS] Soul vent written and encrypted."



def soul_vent_summon(passphrase):
    import os
    from filecrypt import get_fernet, decrypt_file

    journal_dir = os.path.join(os.path.dirname(__file__), "journal")
    if not os.path.exists(journal_dir):
        return [], "[TOMB] No journal entries found."

    fernet = get_fernet(passphrase)
    decrypted_map = {}
    errors = []

    for filename in os.listdir(journal_dir):
        if filename.endswith(".enc"):
            enc_path = os.path.join(journal_dir, filename)
            try:
                decrypted = decrypt_file(enc_path, fernet)
                decrypted_map[filename] = decrypted
            except Exception as e:
                errors.append(f"{filename}: [ERROR] Failed to decrypt: {e}")

    if not decrypted_map:
        return [], "\n".join(errors or ["[TOMB] No decryptable journal entries."])

    return list(decrypted_map.keys()), decrypted_map






def unlock_encrypted_files(directory: str, passphrase: str):
    try:
        previews = []
        for filename in os.listdir(directory):
            if filename.endswith(".enc"):
                path = os.path.join(directory, filename)
                with open(path, "rb") as file:
                    encrypted = file.read()
                fernet = Fernet(passphrase.encode())
                decrypted = fernet.decrypt(encrypted)
                preview = decrypted.decode("utf-8")[:300]  # First 300 chars
                previews.append(f"[FILE] {filename}\n{preview}\n{'-'*40}")
        return "\n\n".join(previews) if previews else "[ERROR] No encrypted files found."
    except Exception as e:
        return f"[ERROR] Failed to unlock files: {e}"


# Placeholder returns for not-yet-refactored menus
def project_protocol():
    return "[TOOL] Project protocol not yet implemented for UI."

def inventory_protocol():
    return "[BOX] Inventory protocol not yet implemented for UI."

def vault_menu(user_input=None):
    """
    GhostVault interactive password manager via text UI.
    Accepts string-based commands from the GhostDrive UI.
    """
    import json
    from cryptography.fernet import Fernet

    vault_path = os.path.join(os.path.dirname(__file__), "vault.enc")
    vault_key_path = os.path.join(os.path.dirname(__file__), "vault.key")

    def get_or_create_key():
        if not os.path.exists(vault_key_path):
            key = Fernet.generate_key()
            with open(vault_key_path, "wb") as f:
                f.write(key)
        else:
            with open(vault_key_path, "rb") as f:
                key = f.read()
        return Fernet(key)

    fernet = get_or_create_key()

    # Load or create empty vault
    if os.path.exists(vault_path):
        try:
            with open(vault_path, "rb") as f:
                decrypted = fernet.decrypt(f.read()).decode()
                vault = json.loads(decrypted)
        except Exception as e:
            return f"[ERROR] Vault error: {e}"
    else:
        vault = {}

    # 
    # Handle commands
    if not user_input or "activate" in user_input.lower():
        return (
            "[LOCK] Vault Protocol Activated.\n"
            "Use one of the following commands:\n"
            "- 'Add password for Gmail'\n"
            "- 'View vault'\n"
            "- 'Delete Gmail'\n"
        )

    # ADD
    elif user_input.lower().startswith("add password for"):
        service = user_input.split("for", 1)[1].strip()
        vault[service] = {
            "username": "example_user",
            "password": "hunter2"
        }
        with open(vault_path, "wb") as f:
            f.write(fernet.encrypt(json.dumps(vault).encode()))
        return f"[SUCCESS] Entry for '{service}' saved (placeholder values used)."

    # VIEW
    elif "view" in user_input.lower() and "vault" in user_input.lower():
        if not vault:
            return " Vault is empty."
        lines = [f"[BOX] Vault contains {len(vault)} entries:"]
        for name in vault:
            lines.append(f"- {name}")
        return "\n".join(lines)

    # DELETE
    elif user_input.lower().startswith("delete"):
        name = user_input.split("delete", 1)[1].strip()
        if name in vault:
            del vault[name]
            with open(vault_path, "wb") as f:
                f.write(fernet.encrypt(json.dumps(vault).encode()))
            return f"[DELETE] Entry '{name}' deleted from vault."
        else:
            return f"[WARNING] Entry '{name}' not found in vault."

    return "[BOT] Command not recognized. Try 'Add password for Gmail' or 'View vault'."





def execute_command(command_name: str, username: str = "User"):
    """
    Central dispatcher for all Jynx UI commands.
    Returns all output as strings for the UI display instead of printing.
    """
    try:
        if command_name == "blackout_mode":
            return blackout_mode()

        elif command_name == "reconnect_wifi":
            return reconnect_wifi()

        elif command_name == "scan_networks":
            return scan_networks()

        elif command_name == "activate_big_brother":
            return activate_big_brother()

        elif command_name == "status_report":
            return status_report()

        elif command_name == "soul_vent":
            return soul_vent()

        elif command_name == "soul_vent_summon":
            return soul_vent_summon()

        elif command_name == "project_protocol":
            return project_protocol()

        elif command_name == "inventory_protocol":
            return inventory_protocol()

        elif command_name == "vault_menu":
            return vault_menu(prompt)


        elif command_name == "unlock_encrypted_files":
            return unlock_encrypted_files(".", "your-passphrase")  # adjust path + passphrase later

        else:
            return f"[WARNING] Unknown protocol: {command_name}"

    except Exception as e:
        return f"[ERROR] Error while executing '{command_name}': {e}"

