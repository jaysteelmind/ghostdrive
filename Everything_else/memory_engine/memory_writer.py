import json
import datetime
import os
import re

MEMORY_PATH = os.path.join("context", "memory.jsonl")

def extract_tags_from_text(text, max_tags=5):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    unique_words = list(dict.fromkeys(words))
    return unique_words[:max_tags]

def is_duplicate(text):
    if not os.path.exists(MEMORY_PATH):
        return False
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("text", "").strip() == text.strip():
                        return True
                except:
                    continue
        return False
    except Exception as e:
        print(f"❌ Error checking duplicates: {e}")
        return False

def write_memory(prompt, memory_path=MEMORY_PATH):
    if not prompt.strip():
        return

    if is_duplicate(prompt):
        print("⚠️ Duplicate memory found. Skipping save.")
        return

    entry = {
        "text": prompt.strip(),
        "tags": extract_tags_from_text(prompt),
        "timestamp": datetime.datetime.now().isoformat()
    }

    try:
        with open(memory_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print("✅ Memory saved.")
    except Exception as e:
        print(f"❌ Failed to write memory: {e}")



