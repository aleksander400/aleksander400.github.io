import json
import os
from datetime import datetime

MEMORY_FILE = "nova_memory_simple.json"

def _load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def _save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f)

def store_memory(key, value, category=None):
    memory = _load_memory()
    memory[key] = {
        'value': value,
        'timestamp': datetime.now().isoformat(),
        'category': category
    }
    _save_memory(memory)
    return f"Zapamiętano: {key}"

def search_memory(query, return_all=False):
    memory = _load_memory()
    results = []
    for key, data in memory.items():
        if query.lower() in key.lower() or query.lower() in data['value'].lower():
            results.append((key, data['value']))
    return results if return_all else (results[0][1] if results else None)

def delete_memory_entries(keyword):
    memory = _load_memory()
    count = 0
    for key in list(memory.keys()):
        if keyword.lower() in key.lower():
            del memory[key]
            count += 1
    _save_memory(memory)
    return f"Usunięto {count} wpisów"

def learn_from_logs(log_file):
    if not os.path.exists(log_file):
        return
    with open(log_file, 'r') as f:
        logs = f.read()
    store_memory("log_patterns", logs[:1000])
