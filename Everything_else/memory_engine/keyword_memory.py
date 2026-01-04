import os
import json

def get_keyword_file_path(memory_dir):
    return os.path.join(memory_dir, "keywords.json")

def load_keywords(memory_dir):
    filepath = get_keyword_file_path(memory_dir)
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def save_keywords(keywords, memory_dir):
    filepath = get_keyword_file_path(memory_dir)
    with open(filepath, 'w') as f:
        json.dump(keywords, f, indent=2)

def update_keyword(term, definition, memory_dir):
    keywords = load_keywords(memory_dir)
    keywords[term] = definition
    save_keywords(keywords, memory_dir)

def get_keyword(term, memory_dir):
    keywords = load_keywords(memory_dir)
    return keywords.get(term)
