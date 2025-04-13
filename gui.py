# gui.py — Cyberpunk AI Panel with Memory Manager
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from interface import listen_to_user, speak_to_user
from llm_core import generate_response
from command_parser import parse_command
from system_agent import execute_system_command
from web_agent import search_web
from file_agent import handle_file_command
from mail_agent import handle_mail_command
from calendar_agent import handle_calendar_command
try:
    from memory_manager import MemoryManager
    memory_manager = MemoryManager()
    store_memory = memory_manager.store_memory
    search_memory = memory_manager.search_memory
    delete_memory_entries = memory_manager.delete_memory_entries
    learn_from_logs = memory_manager.learn_from_logs
except ImportError as e:
    print(f"Błąd importu MemoryManager: {str(e)}")
    # Fallback do prostego systemu pamięci
    from memory_manager_simple import *
from file_analyzer import analyze_file_content
from mail_agent import extract_learning_data_from_emails
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageTk
import sys
import os
import datetime

ICON_PATH = "icon_cyberpunk_glow.png"
AVATAR_PATH = "avatar_nova.png"
AVATAR_GLOW_PATH = "avatar_nova_glow.png"
CHAT_LOG_PATH = "chat_logs.txt"

class AIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nova AI - CyberPanel")
        self.root.geometry("900x600")
        self.root.configure(bg="#0f0f0f")

        if os.path.exists(AVATAR_PATH):
            avatar_img = Image.open(AVATAR_PATH).resize((150, 150))
            self.avatar_photo = ImageTk.PhotoImage(avatar_img)
            self.avatar_label = tk.Label(root, image=self.avatar_photo, bg="#0f0f0f")
            self.avatar_label.pack(side=tk.LEFT, padx=(10, 0), pady=(10, 0))

        frame_right = tk.Frame(root, bg="#1a1a1a")
        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.text_area = scrolledtext.ScrolledText(frame_right, wrap=tk.WORD, width=60, height=20, 
                                                   font=("Consolas", 11), bg="#101010", fg="#00ffcc",
                                                   insertbackground="white")
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        entry_frame = tk.Frame(frame_right, bg="#1a1a1a")
        entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.entry = tk.Entry(entry_frame, width=50, font=("Consolas", 11), bg="#0f0f0f", fg="#00ffcc",
                               insertbackground="#00ffcc")
        self.entry.pack(side=tk.LEFT, padx=(0, 5), ipady=4, fill=tk.X, expand=True)
        self.entry.bind('<Return>', lambda event: self.process_input())

        self.send_button = tk.Button(entry_frame, text="➔", command=self.process_input,
                                     font=("Consolas", 11), bg="#222", fg="#00ffcc", width=4)
        self.send_button.pack(side=tk.LEFT)

        self.listen_button = tk.Button(entry_frame, text="🎤", command=self.listen_thread,
                                       font=("Consolas", 11), bg="#222", fg="#00ffcc", width=4)
        self.listen_button.pack(side=tk.LEFT, padx=(5, 5))

        self.settings_button = tk.Button(entry_frame, text="⚙", command=self.open_settings,
                                         font=("Consolas", 11), bg="#222", fg="#00ffcc", width=4)
        self.settings_button.pack(side=tk.LEFT, padx=(5, 5))

        self.memory_button = tk.Button(entry_frame, text="🧠", command=self.open_memory_manager,
                                       font=("Consolas", 11), bg="#222", fg="#00ffcc", width=4)
        self.memory_button.pack(side=tk.LEFT, padx=(5, 5))

        self.antivirus_button = tk.Button(entry_frame, text="🛡", command=self.open_antivirus_panel,
                                       font=("Consolas", 11), bg="#222", fg="#00ffcc", width=4)
        self.antivirus_button.pack(side=tk.LEFT, padx=(5, 5))

        self.learn_button = tk.Button(entry_frame, text="🎓", command=self.open_learning_center,
                                       font=("Consolas", 11), bg="#222", fg="#00ffcc", width=4)
        self.learn_button.pack(side=tk.LEFT, padx=(5, 5))

        self.quit_button = tk.Button(entry_frame, text="✖", command=self.quit_app,
                                     font=("Consolas", 11), bg="#222", fg="#ff4f4f", width=4)
        self.quit_button.pack(side=tk.RIGHT)

        self.speak("Witaj! Jestem Nova – Twoja cyberpunkowa AI.")
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.tray_icon = None

        threading.Thread(target=self.train_from_logs).start()

    def speak(self, message):
        self.text_area.insert(tk.END, f"Nova: {message}\n")
        self.text_area.see(tk.END)
        self.save_conversation("Nova", message)
        self.animate_avatar(True)
        speak_to_user(message)
        self.root.after(1000, lambda: self.animate_avatar(False))

    def animate_avatar(self, talking):
        img_path = AVATAR_GLOW_PATH if talking else AVATAR_PATH
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((150, 150))
            self.avatar_photo = ImageTk.PhotoImage(img)
            self.avatar_label.configure(image=self.avatar_photo)

    def process_input(self):
        user_input = self.entry.get()
        self.text_area.insert(tk.END, f"Ty: {user_input}\n")
        self.entry.delete(0, tk.END)
        self.save_conversation("Ty", user_input)
        self.handle_command(user_input)

    def listen_thread(self):
        threading.Thread(target=self.listen_and_process).start()

    def listen_and_process(self):
        self.speak("Słucham...")
        user_input = listen_to_user()
        self.text_area.insert(tk.END, f"Ty (głos): {user_input}\n")
        self.save_conversation("Ty (głos)", user_input)
        self.handle_command(user_input)

    def handle_command(self, user_input):
        lowered = user_input.lower()
        if lowered.startswith("usuń z pamięci"):
            keyword = user_input[len("usuń z pamięci"):].strip()
            result = delete_memory_entries(keyword)
            self.speak(result)
            return
        elif lowered.startswith("zapomnij"):
            keyword = user_input[len("zapomnij"):].strip()
            result = delete_memory_entries(keyword)
            self.speak(result)
            return

        memory_response = search_memory(user_input, return_all=False)
        if memory_response:
            output = memory_response
        else:
            intent, params = parse_command(user_input)
            if intent == "system":
                output = execute_system_command(params)
            elif intent == "internet":
                try:
                    output, source_text = search_web(params, return_source=True)
                    if source_text and len(source_text.split()) > 10:
                        store_memory(f"Szukaj: {params}", source_text)
                except Exception:
                    output = search_web(params)
            elif intent == "file":
                output = handle_file_command(params)
                if os.path.isfile(params):
                    content = analyze_file_content(params)
                    if content:
                        store_memory(f"Z pliku: {params}", content)
            elif intent == "mail":
                output = handle_mail_command(params)
                learned = extract_learning_data_from_emails()
                if learned:
                    store_memory("Maile", learned)
            elif intent == "calendar":
                output = handle_calendar_command(params)
            elif intent == "code":
                from code_agent import generate_code
                output = generate_code(params)
                if not output.startswith("[Błąd]"):
                    store_memory(f"Wygenerowany kod: {params[:50]}", output)
            else:
                try:
                    from qa_chatbot import chat_ai
                    output = chat_ai(user_input)
                except Exception:
                    output = generate_response(user_input)
            if output and len(output.split()) > 3:
                store_memory(user_input, output)
        self.speak(output)

    def train_from_logs(self):
        self.speak("Analizuję wcześniejsze rozmowy...")
        learn_from_logs(CHAT_LOG_PATH)

    def save_conversation(self, speaker, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # Ensure proper encoding and clean special characters
            cleaned_message = message.encode('utf-8', errors='replace').decode('utf-8')
            with open(CHAT_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {speaker}: {cleaned_message}\n")
                f.flush()
            
            # Rotate log file if it gets too large (>1MB)
            if os.path.exists(CHAT_LOG_PATH) and os.path.getsize(CHAT_LOG_PATH) > 1000000:
                backup_name = f"{CHAT_LOG_PATH}.{timestamp.replace(' ', '_').replace(':', '-')}.bak"
                os.rename(CHAT_LOG_PATH, backup_name)
        except Exception as e:
            print(f"Błąd zapisu logu: {str(e)}")

    def open_settings(self):
        top = tk.Toplevel(self.root)
        top.title("Ustawienia Nova AI")
        top.geometry("400x300")
        top.configure(bg="#1a1a1a")
        label = tk.Label(top, text="Ustawienia (tryb beta)", fg="#00ffcc", bg="#1a1a1a", font=("Consolas", 13))
        label.pack(pady=10)

    def open_memory_manager(self):
        top = tk.Toplevel(self.root)
        top.title("🧠 Zarządzanie Pamięcią Nova")
        top.geometry("700x400")
        top.configure(bg="#111")

        search_entry = tk.Entry(top, font=("Consolas", 11), bg="#0f0f0f", fg="#00ffcc", insertbackground="#00ffcc")
        search_entry.pack(fill=tk.X, padx=10, pady=5)

        memory_list = scrolledtext.ScrolledText(top, font=("Consolas", 10), bg="#101010", fg="#00ffcc")
        memory_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def refresh_memory():
            memory_list.delete("1.0", tk.END)
            entries = search_memory(search_entry.get(), return_all=True)
            if not entries:
                memory_list.insert(tk.END, "(Brak dopasowań)")
            else:
                for q, a in entries:
                    memory_list.insert(tk.END, f"Q: {q}\nA: {a}\n{'-'*40}\n")

        def delete_memory():
            keyword = search_entry.get()
            if messagebox.askyesno("Potwierdzenie", f"Usunąć wszystkie wpisy zawierające: '{keyword}'?"):
                delete_memory_entries(keyword)
                refresh_memory()

        button_frame = tk.Frame(top, bg="#111")
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(button_frame, text="🔄 Odśwież", command=refresh_memory,
                  font=("Consolas", 10), bg="#222", fg="#00ffcc").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="❌ Usuń", command=delete_memory,
                  font=("Consolas", 10), bg="#222", fg="#ff4f4f").pack(side=tk.LEFT, padx=5)

        refresh_memory()

    def open_antivirus_panel(self):
        top = tk.Toplevel(self.root)
        top.title("🛡 Panel Antywirusowy Nova")
        top.geometry("600x400")
        top.configure(bg="#111")

        scan_button = tk.Button(top, text="🔍 Skanuj system", 
                              command=lambda: self.run_antivirus_scan(top),
                              font=("Consolas", 12), bg="#222", fg="#00ffcc")
        scan_button.pack(pady=20)

        results_area = scrolledtext.ScrolledText(top, font=("Consolas", 10), 
                                               bg="#101010", fg="#00ffcc")
        results_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        results_area.insert(tk.END, "Kliknij 'Skanuj system' aby rozpocząć\n")

    def run_antivirus_scan(self, window):
        from antivirus_agent_ai import scan_system
        
        # Wyczyść obszar wyników
        for widget in window.winfo_children():
            if isinstance(widget, scrolledtext.ScrolledText):
                text_area = widget
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, "Skanowanie w toku...")
                text_area.tag_configure("danger", foreground="#ff5555")
                text_area.tag_configure("warning", foreground="#ffcc00")
                text_area.tag_configure("safe", foreground="#00ff99")
        
        # Uruchom skanowanie w osobnym wątku
        def scan_thread():
            results = scan_system()
            window.after(0, lambda: self.display_scan_results(window, results))
            
        threading.Thread(target=scan_thread).start()
        
    def display_scan_results(self, window, results):
        for widget in window.winfo_children():
            if isinstance(widget, scrolledtext.ScrolledText):
                text_area = widget
                text_area.delete("1.0", tk.END)
                
                lines = results.split('\n')
                for line in lines:
                    if line.startswith('[!]') or 'WYKRYTO ZAGROŻENIA' in line:
                        text_area.insert(tk.END, line + '\n', "danger")
                    elif line.startswith('[?]') or 'PODEJRZANE' in line:
                        text_area.insert(tk.END, line + '\n', "warning")
                    elif 'Nie znaleziono' in line:
                        text_area.insert(tk.END, line + '\n', "safe")
                    else:
                        text_area.insert(tk.END, line + '\n')

    def open_learning_center(self):
        top = tk.Toplevel(self.root)
        top.title("🎓 Centrum Nauki Nova")
        top.geometry("600x400")
        top.configure(bg="#111")

        label = tk.Label(top, text="Centrum Nauki AI", 
                        font=("Consolas", 14), bg="#111", fg="#00ffcc")
        label.pack(pady=10)

        text_area = scrolledtext.ScrolledText(top, font=("Consolas", 10), 
                                            bg="#101010", fg="#00ffcc")
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        text_area.insert(tk.END, "Funkcjonalność centrum nauki w budowie...")

    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
        sys.exit()

    def minimize_to_tray(self):
        self.root.withdraw()
        if os.path.exists(ICON_PATH):
            image = Image.open(ICON_PATH)
        else:
            image = Image.new('RGB', (64, 64), color=(73, 109, 137))
            draw = ImageDraw.Draw(image)
            draw.rectangle((16, 16, 48, 48), fill="white")

        menu = (item('Pokaż', self.restore_window), item('Zamknij', self.quit_app))
        self.tray_icon = pystray.Icon("ai_tray", image, "Nova AI Panel", menu)
        threading.Thread(target=self.tray_icon.run).start()

    def restore_window(self, icon=None, item=None):
        self.root.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
        self.tray_icon = None

if __name__ == "__main__":
    root = tk.Tk()
    app = AIApp(root)
    root.mainloop()
