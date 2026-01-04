import os, csv
import json
from cryptography.fernet import Fernet

# ──────────────────────────────────────────────
# 🔒 Dynamic, User-Defined Inventory Manager
# ──────────────────────────────────────────────

INVENTORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "inventory"))
os.makedirs(INVENTORY_DIR, exist_ok=True)


def get_inventory_path(username):
    """Return full path to the encrypted inventory file for this user."""
    return os.path.join(INVENTORY_DIR, f"inventory_{username}.enc")


# Default starting schema (can be expanded by user)
DEFAULT_SCHEMA = ["name", "quantity", "location", "last_checked"]


def load_inventory(username, fernet: Fernet):
    """Load inventory and schema. Supports both old and new formats."""
    filepath = get_inventory_path(username)
    if not os.path.exists(filepath):
        # No file yet: create base schema and empty data
        return {"schema": DEFAULT_SCHEMA.copy(), "data": []}

    try:
        with open(filepath, "rb") as f:
            decrypted = fernet.decrypt(f.read()).decode("utf-8")
            payload = json.loads(decrypted)

            # Backward compatibility for old list-only format
            if isinstance(payload, list):
                return {"schema": DEFAULT_SCHEMA.copy(), "data": payload}

            # Ensure schema and data keys exist
            if "schema" not in payload or "data" not in payload:
                payload = {"schema": DEFAULT_SCHEMA.copy(), "data": []}

            return payload
    except Exception as e:
        print(f"[ERROR] Failed to decrypt inventory for {username}: {e}")
        return {"schema": DEFAULT_SCHEMA.copy(), "data": []}


def save_inventory(username, payload, fernet: Fernet):
    """Save full inventory payload (schema + data)."""
    filepath = get_inventory_path(username)
    try:
        encrypted = fernet.encrypt(json.dumps(payload, indent=2).encode("utf-8"))
        with open(filepath, "wb") as f:
            f.write(encrypted)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save inventory for {username}: {e}")
        return False


# ──────────────────────────────────────────────
# 📤 Export / Import
# ──────────────────────────────────────────────

def export_inventory_to_csv(payload, path=None):
    import csv

    data = payload.get("data", [])
    schema = payload.get("schema", DEFAULT_SCHEMA)

    # Collect all unique keys from data rows
    all_keys = set(schema)
    for row in data:
        if isinstance(row, dict):
            all_keys.update(row.keys())

    all_keys = list(all_keys)

    if path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "inventory"))
        path = os.path.join(base_dir, "inventory_export.csv")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

    print(f"[INFO] Inventory exported to {path}")
    return path



def import_inventory_from_csv(username, fernet: Fernet, payload_ref: dict, path=None):
    """Import CSV rows into current data set, matching schema fields."""
    try:
        if path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.abspath(os.path.join(base_dir, "..", "Everything_else", "inventory", "inventory_export.csv"))

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Add any new headers to schema automatically
        for field in reader.fieldnames:
            if field not in payload_ref["schema"]:
                payload_ref["schema"].append(field)

        payload_ref["data"].clear()
        payload_ref["data"].extend(rows)
        save_inventory(username, payload_ref, fernet)
        print(f"[INFO] Imported {len(rows)} items from {path}.")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        raise
