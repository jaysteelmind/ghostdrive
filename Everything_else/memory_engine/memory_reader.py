import json

def recall_memory(memory_file_path):
    try:
        with open(memory_file_path, "r") as f:
            lines = f.readlines()
            memories = [json.loads(line.strip()) for line in lines if line.strip()]
        facts = [mem["fact"] for mem in memories]
        return "\n".join(facts)
    except FileNotFoundError:
        return "Memory file not found."
    except Exception as e:
        return f"Error loading memory: {str(e)}"
