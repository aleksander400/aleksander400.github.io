import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from app_controller import AppController
from interface import speak_to_user

class NovaAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nova AI - CyberPanel")
        self.root.geometry("900x600")
        self.root.configure(bg="#0f0f0f")
        
        # Initialize controller
        self.controller = AppController()
        
        # Setup GUI
        self.setup_ui()
        self.speak("Witaj! Jestem Nova - Twój asystent AI.")

    def setup_ui(self):
        # Main text area
        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=80, height=20,
            font=("Consolas", 10), bg="#101010", fg="#00ffcc"
        )
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#1a1a1a")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Buttons
        buttons = [
            ("🛡 Antywirus", self.run_antivirus),
            ("💬 Chatbot", self.run_chatbot),
            ("📊 Monitoring", self.run_monitoring),
            ("⚙ Ustawienia", self.open_settings)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                button_frame, text=text, command=command,
                font=("Consolas", 10), bg="#222", fg="#00ffcc",
                activebackground="#333", activeforeground="#00ff99"
            )
            btn.pack(side=tk.LEFT, padx=5, pady=2)

    def run_antivirus(self):
        """Run antivirus scan with visual feedback"""
        self.clear_output()
        self.print_output("Rozpoczynam skanowanie antywirusowe...")
        self.speak("Rozpoczynam skanowanie systemu.")
        
        def scan():
            try:
                result = self.controller.run_antivirus()
                self.print_output(f"\nWyniki skanowania:\n{result}")
                self.speak("Skanowanie zakończone pomyślnie.")
            except Exception as e:
                self.print_output(f"\nBłąd: {str(e)}", error=True)
                self.speak("Wystąpił błąd podczas skanowania.")
                
        threading.Thread(target=scan, daemon=True).start()

    def run_chatbot(self):
        """Run chatbot interaction"""
        self.clear_output()
        self.print_output("Inicjuję chatbota...")
        self.speak("Gotowy do rozmowy.")
        
        def chat():
            try:
                response = self.controller.run_chatbot()
                self.print_output(f"\nChatbot:\n{response}")
                self.speak("Oto odpowiedź chatbota.")
            except Exception as e:
                self.print_output(f"\nBłąd: {str(e)}", error=True)
                self.speak("Problem z chatbotem.")
                
        threading.Thread(target=chat, daemon=True).start()

    def run_monitoring(self):
        """Run system monitoring"""
        self.clear_output()
        self.print_output("Uruchamiam monitoring systemu...")
        
        def monitor():
            try:
                result = self.controller.monitor_system()
                self.print_output(f"\nStatus systemu:\n{result}")
            except Exception as e:
                self.print_output(f"\nBłąd: {str(e)}", error=True)
                
        threading.Thread(target=monitor, daemon=True).start()

    def open_settings(self):
        """Open settings panel"""
        messagebox.showinfo("Ustawienia", "Panel konfiguracji w budowie")

    def clear_output(self):
        """Clear the text output"""
        self.text_area.delete(1.0, tk.END)

    def print_output(self, text, error=False):
        """Print text to output with formatting"""
        tag = "error" if error else "normal"
        self.text_area.insert(tk.END, text + "\n", tag)
        self.text_area.see(tk.END)
        
    def speak(self, message):
        """Speak message using TTS"""
        try:
            speak_to_user(message)
        except Exception as e:
            self.print_output(f"Błąd syntezy mowy: {str(e)}", error=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = NovaAIApp(root)
    
    # Configure text tags
    app.text_area.tag_config("error", foreground="#ff5555")
    app.text_area.tag_config("normal", foreground="#00ffcc")
    
    root.mainloop()
