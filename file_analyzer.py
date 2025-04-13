# file_analyzer.py
import os
import re
from typing import Optional

def analyze_file_content(file_path: str) -> Optional[str]:
    """Analizuje zawartość pliku i zwraca kluczowe informacje"""
    if not os.path.exists(file_path):
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Prosta analiza dla plików tekstowych
        if len(content) > 1000:
            # Znajdź kluczowe frazy
            sentences = re.split(r'[.!?]', content)
            important = [s.strip() for s in sentences if len(s.split()) > 5 and any(w in s.lower() for w in ['ważne', 'kluczowe', 'podsumowanie'])]
            return '\n'.join(important[:3]) if important else content[:500]
        return content
    except Exception:
        return None
