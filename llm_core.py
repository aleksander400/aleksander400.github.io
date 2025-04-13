import openai
import os
from memory_manager import search_memory

# Konfiguracja API OpenAI
OPENAI_KEY = os.getenv("OPENAI_API_KEY") or "your-api-key-here"
MODEL = "gpt-3.5-turbo"

def generate_response(prompt, context=None):
    """Generate AI response using OpenAI API with memory context"""
    if not OPENAI_KEY or OPENAI_KEY == "your-api-key-here":
        return "Błąd: Brak klucza API OpenAI. Skonfiguruj OPENAI_API_KEY."
    
    # Sprawdź pamięć dla kontekstu
    memory_context = search_memory(prompt, return_all=True)
    memory_str = "\n".join([f"Pamięć: {q}\nOdpowiedź: {a}" for q, a in memory_context]) if memory_context else ""
    
    messages = [
        {"role": "system", "content": "Jesteś Nova - cyberpunkową asystentką AI. Mówisz po polsku."},
        {"role": "system", "content": memory_str},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Błąd API: {str(e)}"
