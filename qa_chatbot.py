# qa_chatbot.py

# Słownik prostych odpowiedzi (możesz rozbudowywać)
qa_pairs = {
    "jak się masz": "Dobrze, dzięki że pytasz.",
    "kim jesteś": "Jestem Nova – Twoja cyberpunkowa asystentka.",
    "co potrafisz": "Pomagam w zarządzaniu systemem, plikami, mailem i więcej.",
    "powiedz żart": "Dlaczego komputer nie może się zakochać? Bo ma za dużo RAM-u na emocje."
}

def chat_ai(user_input: str) -> str:
    user_input = user_input.lower().strip()

    for question, answer in qa_pairs.items():
        if question in user_input:
            return answer

    # Fallback jeśli nie rozumiem
    return "Hmm... jeszcze się uczę. Możesz zadać pytanie inaczej?"
