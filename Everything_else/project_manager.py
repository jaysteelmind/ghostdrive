import os
import json

def load_project_file(filepath, fernet):
    try:
        with open(filepath, "rb") as f:
            encrypted = f.read()
        decrypted = fernet.decrypt(encrypted).decode("utf-8")
        return json.loads(decrypted)
    except Exception as e:
        print(f"[ERROR] Failed to decrypt project file {filepath}: {e}")
        return None

def save_project_file(data, fernet):
    try:
        project_name = data.get("project", "untitled_project").replace(" ", "_")
        filename = f"{project_name}.enc"
        projects_dir = PROJECTS_DIR
        filepath = os.path.join(projects_dir, filename)
        with open(filepath, "wb") as f:
            encrypted = fernet.encrypt(json.dumps(data, indent=2).encode("utf-8"))
            f.write(encrypted)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save project: {e}")
        return False

def delete_project_file(filepath):
    try:
        os.remove(filepath)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to delete project file {filepath}: {e}")
        return False

PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "projects"))
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Optional utility to list encrypted project files
def list_project_files():
    return [f for f in os.listdir(PROJECTS_DIR) if f.endswith(".enc")]