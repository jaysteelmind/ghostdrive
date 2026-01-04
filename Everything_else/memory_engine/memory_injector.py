import atexit

def inject_memory(memory_file_path):
    import os
    import getpass
    from filecrypt import get_fernet, decrypt_file

    if memory_file_path.endswith(".enc"):
        decrypted_path = memory_file_path.replace(".enc", "")
        passphrase = getpass.getpass("🔐 Enter passphrase to decrypt memory: ")
        fernet = get_fernet(passphrase)
        try:
            decrypted = decrypt_file(memory_file_path, fernet)
            with open(decrypted_path, "w", encoding="utf-8") as f:
                f.write(decrypted)
            memory_file_path = decrypted_path
        except Exception as e:
            return f"❌ Memory decryption failed: {e}"

    try:
        with open(memory_file_path, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()

        tagged_lines = []
        for line in raw_lines:
            if "::" in line:
                _, content = line.split("::", 1)
                content = content.strip()
                if content.lower().startswith("you:"):
                    tagged_lines.append(f"USER: {content[4:].strip()}")
                elif content.lower().startswith("jynx:"):
                    tagged_lines.append(f"JYNX: {content[5:].strip()}")
                else:
                    tagged_lines.append(f"USER: {content}")  # fallback
        return "\n".join(tagged_lines) if tagged_lines else "No user memory available."

    except Exception:
        return "No user memory available."


@atexit.register
def cleanup_decrypted_memory():
    try:
        if os.path.exists(decrypted_path):
            os.remove(decrypted_path)
    except:
        pass
