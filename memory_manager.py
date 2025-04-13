import json
import os
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MEMORY_FILE = "nova_memory.json"
EMBEDDING_MODEL = SentenceTransformer('allegro/herbert-base-cased')

# Singleton instance
_memory_manager_instance = None

def get_memory_manager():
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance

# Module-level function for search_memory
def search_memory(query, threshold=0.7, return_all=False):
    return get_memory_manager().search_memory(query, threshold, return_all)

class MemoryManager:
    def __init__(self):
        self.memory = self._load_memory()
        self.embeddings = {}
        self._load_embeddings()

    def _load_memory(self):
        default_memory = {"entries": {}, "categories": {}, "embeddings": {}}
        if not os.path.exists(MEMORY_FILE):
            return default_memory
        try:
            with open(MEMORY_FILE, 'r') as f:
                loaded = json.load(f)
                # Ensure all required keys exist
                for key in ["entries", "categories", "embeddings"]:
                    if key not in loaded:
                        loaded[key] = {}
                return loaded
        except:
            return default_memory

    def _load_embeddings(self):
        if "embeddings" in self.memory:
            self.embeddings = {
                k: np.array(v) for k, v in self.memory["embeddings"].items()
            }

    def _save_memory(self):
        self.memory["embeddings"] = {
            k: v.tolist() for k, v in self.embeddings.items()
        }
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.memory, f)

    def store_memory(self, key, value, category=None):
        embedding = EMBEDDING_MODEL.encode(key + " " + value)
        self.memory["entries"][key] = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'category': category
        }
        self.embeddings[key] = embedding
        
        if category:
            if category not in self.memory["categories"]:
                self.memory["categories"][category] = []
            self.memory["categories"][category].append(key)
        
        self._save_memory()
        return f"Zapamiętano: {key} (kategoria: {category})"

    def search_memory(self, query, threshold=0.7, return_all=False):
        query_embedding = EMBEDDING_MODEL.encode(query)
        results = []
        
        for key, emb in self.embeddings.items():
            similarity = cosine_similarity(
                [query_embedding], 
                [emb]
            )[0][0]
            if similarity > threshold:
                entry = self.memory["entries"][key]
                results.append((key, entry['value'], similarity))
        
        results.sort(key=lambda x: x[2], reverse=True)
        
        if return_all:
            return [(k, v) for k, v, _ in results]
        return results[0][1] if results else None

    def delete_memory_entries(self, keyword):
        count = 0
        for key in list(self.memory["entries"].keys()):
            if keyword.lower() in key.lower():
                del self.memory["entries"][key]
                if key in self.embeddings:
                    del self.embeddings[key]
                count += 1
        self._save_memory()
        return f"Usunięto {count} wpisów"

    def learn_from_logs(self, log_file):
        if not os.path.exists(log_file):
            return
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.read()
            self.store_memory("log_patterns", logs[:2000], "system")
        except UnicodeDecodeError:
            with open(log_file, 'r', encoding='cp1250') as f:
                logs = f.read()
            self.store_memory("log_patterns", logs[:2000], "system")
