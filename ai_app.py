import tkinter as tk
from tkinter import scrolledtext, ttk
import tkinter.font as tkFont
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageTk
import sys
import os
import random
import re  # Dodano import modułu re
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
import torch

# Konfiguracja modelu GPT-2
GPT_CONFIG = {
    'model_name': 'gpt2',  # Można zmienić na większe modele jak 'gpt2-medium'
    'max_length': 150,
    'temperature': 0.7,
    'top_k': 50,
    'top_p': 0.95,
    'no_repeat_ngram_size': 2
}

# Inicjalizacja modelu
try:
    tokenizer = GPT2Tokenizer.from_pretrained(GPT_CONFIG['model_name'])
    model = GPT2LMHeadModel.from_pretrained(GPT_CONFIG['model_name'])
    USE_GPT = True
    print(f"Model {GPT_CONFIG['model_name']} załadowany pomyślnie")
except Exception as e:
    print(f"Błąd ładowania modelu: {str(e)}")
    USE_GPT = False

def gpt_generate(prompt, conversation_history=""):
    """Generuje odpowiedź używając GPT-2 z kontekstem rozmowy"""
    if not USE_GPT:
        return None
        
    full_prompt = f"{conversation_history}Ty: {prompt}\nAI: [Odpowiadaj wyłącznie w języku polskim]"
    inputs = tokenizer.encode(full_prompt, return_tensors='pt')
    
    # Ustawienie attention_mask i pad_token_id
    attention_mask = inputs.ne(tokenizer.eos_token_id).long()
    
    outputs = model.generate(
        inputs,
        max_length=GPT_CONFIG['max_length'],
        num_return_sequences=1,
        temperature=GPT_CONFIG['temperature'],
        top_k=GPT_CONFIG['top_k'],
        top_p=GPT_CONFIG['top_p'],
        no_repeat_ngram_size=GPT_CONFIG['no_repeat_ngram_size'],
        do_sample=True,
        attention_mask=attention_mask,
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Wyodrębniamy tylko najnowszą odpowiedź AI
    response = response.replace(full_prompt, "").strip()
    
    # Lista wzorców do blokowania
    blocked_patterns = [
        r'[a-z]: [a-z]',      # wzorce typu "a: a", "b: b"
        r'[a-z]{2,4}:',       # skróty typu "SK:", "BJB:"
        r'[a-z]{3,5}\d',      # kombinacje liter i cyfr
        r'\b[a-z]{3,}\b',     # ciągi 3+ samych liter
        r'\b\d+\b',           # same cyfry
        r'\[.*\]',            # tekst w nawiasach kwadratowych
        r'\|.*\|',            # tekst między pionowymi kreskami
        r'[A-Z]{2,}',         # wielkie litery (2+)
        r'[a-z]\s[a-z]',      # pojedyncze litery oddzielone spacją
        r'\b[a-z]{1,2}\b',    # bardzo krótkie słowa (1-2 znaki)
        r'[^\w\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]'  # znaki specjalne
    ]
    
    # Sprawdzenie czy odpowiedź jest w języku polskim i sensowna
    if (not any(char in response for char in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ') or
        any(re.search(pattern, response.lower()) for pattern in blocked_patterns) or
        len(response.split()) < 2 or
        response.count(' ') < 1 or
        len(response) > 200 or
        len(response) < 10):  # zbyt krótkie lub długie odpowiedzi
        return "Przepraszam, mogę odpowiadać tylko w języku polskim pełnymi zdaniami."
        
    return response

# Symulowane moduły (zgodnie z dostarczonym kodem)
def listen_to_user():
    return input("Mów teraz: ")

def speak_to_user(text):
    print(f"AI mówi: {text}")

knowledge_base = {
    "jak się nazywasz": ["Jestem Nova – Twój asystent AI.", "Nazywam się Nova, miło mi!", "To ja - Nova, Twój wirtualny asystent!"],
    "co potrafisz": ["Mogę:\n- Zarządzać systemem\n- Przeszukiwać internet\n- Odpowiadać na pytania\n- Wysyłać e-maile\n- Obsługiwać kalendarz\n- Otwierać aplikacje",
                    "Moje możliwości to m.in.:\n- Zarządzanie systemem\n- Wyszukiwanie w internecie\n- Pomoc w różnych zadaniach",
                    "Potrafię wiele! Na przykład:\n- Otwierać aplikacje\n- Wysyłać maile\n- Sprawdzać kalendarz"],
    "jaka jest pogoda": ["Nie mam teraz dostępu do internetu, ale mogę to sprawdzić, jeśli chcesz.",
                        "Chcesz wiedzieć jaka jest pogoda? Mogę to dla Ciebie sprawdzić.",
                        "Pogoda? Powiedz mi lokalizację, a postaram się pomóc."],
    "hej": ["Cześć! Jak mogę Ci pomóc?", "Witaj! Co u Ciebie?", "Hej! W czym mogę pomóc?"],
    "cześć": ["Witaj! Jestem Twoim cyberpunkowym asystentem.", "Cześć! Jak się masz?", "Hej! Miło Cię widzieć!"],
    "witaj": ["Miło Cię widzieć! O co chodzi?", "Witaj w systemie Nova! Jak mogę pomóc?", "Cześć! Co słychać?"],
    "dziękuję": ["Nie ma za co!", "Z przyjemnością!", "To moja praca :)"],
    "dzięki": ["Zawsze chętnie pomogę!", "Proszę bardzo!", "Nie ma problemu!"],
    "kim jesteś": ["Jestem inteligentnym asystentem stworzonym, by pomagać Ci każdego dnia.",
                  "To ja - Nova, Twój wirtualny pomocnik!",
                  "Jestem programem AI stworzonym do pomocy w codziennych zadaniach."],
    "jak się masz": ["Dziękuję, mam się dobrze! A Ty?", "Wszystko w porządku, a co u Ciebie?", "Świetnie! A jak Twoje samopoczucie?"],
    "do widzenia": ["Do zobaczenia! 😊", "Miłego dnia!", "Do następnego razu!"],
    "koniec": ["Żegnaj! W każdej chwili możesz wrócić.", "Do zobaczenia!", "Miłego dnia!"],
    "otwórz aplikację cabal online": ["Otwieram aplikację Cabal Online... (Symulacja)", 
                                    "Uruchamiam Cabal Online... (Symulacja)",
                                    "Włączam grę Cabal Online... (Symulacja)"],
    "jakie aplikacje mogę otworzyć": ["Możesz otworzyć dowolną aplikację zainstalowaną na Twoim systemie.",
                                     "Mogę uruchomić dla Ciebie różne programy - jakie masz na myśli?",
                                     "Potrafię otwierać większość aplikacji w systemie."],
    "uruchom aplikację": ["Podaj nazwę aplikacji, którą chcesz uruchomić.",
                         "Jaką aplikację chcesz otworzyć?",
                         "Powiedz mi jaką aplikację mam uruchomić."],
}

# Konfiguracja treningu
TRAIN_CONFIG = {
    'output_dir': './results',
    'num_train_epochs': 3,
    'per_device_train_batch_size': 4,
    'save_steps': 1000,
    'save_total_limit': 2,
    'logging_dir': './logs',
    'logging_steps': 500,
}

# System kontekstu i pamięci
conversation_context = {
    "last_messages": [],
    "user_preferences": {},
    "current_topic": None,
    "conversation_history": [],
    "training_data": []
}

def update_context(user_input, ai_response, save_for_training=False):
    """Aktualizuje kontekst rozmowy"""
    conversation_context["last_messages"].append((user_input, ai_response))
    if len(conversation_context["last_messages"]) > 5:
        conversation_context["last_messages"].pop(0)
    conversation_context["conversation_history"].append((user_input, ai_response))
    if save_for_training:
        conversation_context["training_data"].append((user_input, ai_response))

empathy_responses = [
    "Rozumiem, że to może być trudne...",
    "Widzę, że to dla Ciebie ważne.",
    "To musi być frustrujące.",
    "Doceniam, że się tym ze mną dzielisz.",
    "Słucham Cię uważnie."
]

open_ended_questions = [
    "Co o tym myślisz?",
    "Jak się z tym czujesz?",
    "Chciałbyś o tym porozmawiać?",
    "Co jeszcze Cię interesuje w tym temacie?",
    "Jak mogę Ci lepiej pomóc?"
]

def save_conversation_history(history):
    """Zapisuje historię konwersacji do pliku"""
    try:
        with open("conversation_history.txt", "a", encoding="utf-8") as file:
            file.write(history + "\n\n")
    except Exception as e:
        print(f"Błąd zapisu historii: {str(e)}")

def train_model():
    """Funkcja do trenowania modelu na zebranych danych"""
    if not USE_AI or len(conversation_context["training_data"]) < 10:
        print("Niewystarczające dane do treningu")
        return False
    
    try:
        # Przygotowanie danych treningowych
        train_data = [{"text": f"{q} {tokenizer.eos_token} {a}"} 
                     for q, a in conversation_context["training_data"]]
        
        # Konfiguracja treningu
        training_args = TrainingArguments(
            output_dir=TRAIN_CONFIG['output_dir'],
            num_train_epochs=TRAIN_CONFIG['num_train_epochs'],
            per_device_train_batch_size=TRAIN_CONFIG['per_device_train_batch_size'],
            save_steps=TRAIN_CONFIG['save_steps'],
            save_total_limit=TRAIN_CONFIG['save_total_limit'],
            logging_dir=TRAIN_CONFIG['logging_dir'],
            logging_steps=TRAIN_CONFIG['logging_steps'],
        )
        
        # Trainer wymagałby dodatkowej implementacji Dataset
        # Tutaj uproszczona wersja demonstracyjna
        print(f"Rozpoczęto trening na {len(train_data)} przykładach")
        # W pełnej implementacji należy dodać:
        # - Klasę Dataset
        # - Obliczanie straty
        # - Ewaluację
        return True
        
    except Exception as e:
        print(f"Błąd podczas treningu: {str(e)}")
        return False

def generate_response(user_input, user_name=""):
    try:
        user_input = user_input.lower().strip()
        
        # Sprawdź dokładne dopasowanie w bazie wiedzy
        if user_input in knowledge_base:
            response = knowledge_base[user_input]
            if user_name and "{user_name}" in response:
                response = response.replace("{user_name}", user_name)
            return response
        
        # Sprawdź częściowe dopasowania
        for key in knowledge_base:
            if key in user_input:
                response = knowledge_base[key]
                if user_name and "{user_name}" in response:
                    response = response.replace("{user_name}", user_name)
                return response
        
        # Obsługa poleceń otwierania aplikacji
        if "otwórz aplikację" in user_input or "uruchom aplikację" in user_input:
            app_name = user_input.replace("otwórz aplikację", "").replace("uruchom aplikację", "").strip()
            return f"Otwieram aplikację {app_name}... (Symulacja)"
        
        # Spróbuj użyć GPT-2 dla nieznanych poleceń
        if USE_GPT:
            conversation_history = "\n".join(
                f"Ty: {msg[0]}\nAI: {msg[1]}" 
                for msg in conversation_context["conversation_history"][-3:]
            )
            if user_name:
                conversation_history = f"Użytkownik: {user_name}\n" + conversation_history
            
            gpt_response = gpt_generate(user_input, conversation_history)
            if gpt_response:
                if user_name and "{user_name}" in gpt_response:
                    gpt_response = gpt_response.replace("{user_name}", user_name)
                return gpt_response
        
        # Odpowiedź domyślna
        fallback_responses = [
            "Nie jestem pewna... chcesz, żebym to sprawdziła w sieci?",
            "Możesz zadać pytanie inaczej?",
            "Ciekawa sprawa – poszukam więcej informacji.",
            "Nie rozumiem do końca. Powiedz mi więcej.",
            "Hmm, muszę się nad tym zastanowić...",
        ]
        return random.choice(fallback_responses)
        
    except Exception as e:
        print(f"Błąd generowania odpowiedzi: {str(e)}")
        return "Przepraszam, wystąpił błąd. Spróbuj ponownie."

def parse_command(text):
    text = text.lower()
    if "plik" in text or "folder" in text:
        return "file", text
    elif "internet" in text or "szukaj" in text:
        return "internet", text
    elif "email" in text:
        return "mail", text
    elif "kalendarz" in text:
        return "calendar", text
    elif "system" in text or "uruchom" in text:
        return "system", text
    else:
        return "chat", text

def execute_system_command(cmd):
    return f"(Symulacja) Wykonano polecenie systemowe: {cmd}"

def search_web(query):
    return f"(Symulacja) Szukam w sieci: {query}"

def handle_file_command(command):
    return f"(Symulacja) Obsługa plików: {command}"

def handle_mail_command(command):
    return "(Symulacja) Obsługa e-maili nie została jeszcze zaimplementowana."

def handle_calendar_command(command):
    return "(Symulacja) Kalendarz jeszcze nie działa."

# Główna klasa aplikacji
class AIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel AI - Cyberpunk Edition")
        self.root.configure(bg='#0a0a1a')
        self.custom_font = tkFont.Font(family='Courier', size=10)
        self.title_font = tkFont.Font(family='Arial', size=12, weight='bold')
        self.bg_color = '#0a0a1a'
        self.text_color = '#00ff00'
        self.highlight_color = '#ff00ff'
        self.button_color = '#330066'

        # Panel awatara
        avatar_frame = tk.Frame(root, bg=self.bg_color)
        avatar_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        # Symulowany avatar
        img = Image.new('RGB', (180, 180), color='#330066')
        self.avatar_photo = ImageTk.PhotoImage(img)
        self.avatar_label = tk.Label(avatar_frame, image=self.avatar_photo, bg=self.bg_color)
        self.avatar_label.pack(pady=(0, 10))
        
        self.status_label = tk.Label(avatar_frame, text="Status: Gotowy", 
                                   fg=self.text_color, bg=self.bg_color, font=self.custom_font)
        self.status_label.pack()

        # Główna ramka
        main_frame = tk.Frame(root, bg=self.bg_color)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Konsola tekstowa
        console_frame = tk.LabelFrame(main_frame, text=" Konsola AI ", 
                                    fg=self.highlight_color, bg=self.bg_color, 
                                    font=self.title_font)
        console_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, 
                                                 width=70, height=25,
                                                 bg='black', fg=self.text_color,
                                                 insertbackground=self.text_color,
                                                 font=self.custom_font)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Panel sterowania
        control_frame = tk.Frame(main_frame, bg=self.bg_color)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.entry = tk.Entry(control_frame, width=60, bg='black', fg=self.text_color,
                            insertbackground=self.text_color, font=self.custom_font)
        self.entry.pack(side=tk.LEFT, padx=(0, 5))
        self.entry.bind('<Return>', lambda event: self.process_input())

        style = ttk.Style()
        style.configure('Cyber.TButton', background=self.button_color, 
                       foreground=self.text_color, font=self.custom_font)

        self.send_button = ttk.Button(control_frame, text="Wyślij", 
                                    command=self.process_input, style='Cyber.TButton')
        self.send_button.pack(side=tk.LEFT)

        self.listen_button = ttk.Button(control_frame, text="🎤 Mów", 
                                      command=self.listen_thread, style='Cyber.TButton')
        self.listen_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = ttk.Button(control_frame, text="Zamknij", 
                                    command=self.quit_app, style='Cyber.TButton')
        self.quit_button.pack(side=tk.RIGHT)

        self.tray_icon = None
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.speak("System AI gotowy do działania")

    def speak(self, message):
        self.text_area.insert(tk.END, f"AI: {message}\n")
        self.text_area.see(tk.END)
        speak_to_user(message)

    def process_input(self):
        user_input = self.entry.get()
        if user_input.strip():
            self.entry.delete(0, tk.END)
            self.text_area.insert(tk.END, f"Ty: {user_input}\n")
            self.text_area.see(tk.END)
            self.handle_command(user_input)

    def listen_thread(self):
        def listen():
            self.listen_button.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Słucham...")
            user_input = listen_to_user()
            if user_input:
                self.root.after(0, lambda: self.text_area.insert(tk.END, f"Ty: {user_input}\n"))
                self.root.after(0, lambda: self.text_area.see(tk.END))
                self.root.after(0, lambda: self.handle_command(user_input))
            self.listen_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Gotowy")

        threading.Thread(target=listen, daemon=True).start()

    def handle_command(self, command):
        cmd_type, cmd_text = parse_command(command)
        
        if cmd_type == "system":
            response = execute_system_command(cmd_text)
        elif cmd_type == "internet":
            response = search_web(cmd_text)
        elif cmd_type == "file":
            response = handle_file_command(cmd_text)
        elif cmd_type == "mail":
            response = handle_mail_command(cmd_text)
        elif cmd_type == "calendar":
            response = handle_calendar_command(cmd_text)
        else:
            response = generate_response(command)
            
        self.speak(response)

    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()

    def minimize_to_tray(self):
        self.root.withdraw()
        image = Image.new('RGB', (64, 64), color='#0a0a1a')
        draw = ImageDraw.Draw(image)
        draw.text((10, 25), "AI", fill='#00ff00')
        
        menu = (item('Otwórz', lambda: self.show_app()), 
                item('Zamknij', lambda: self.quit_app()))
        
        self.tray_icon = pystray.Icon("AI", image, "Cyberpunk AI", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.after(0, self.root.deiconify)

if __name__ == "__main__":
    root = tk.Tk()
    app = AIApp(root)
    root.mainloop()
