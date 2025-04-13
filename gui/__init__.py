# Moduł GUI - rozbudowana wersja
from tkinter import Tk, Frame, Label, Button, Menu, messagebox
from antivirus import scan_files, analyze_threats
from search import safe_search
from ai import generate_response

class AntywirusGUI:
    def __init__(self, master):
        self.master = master
        master.title("AI Antywirus-Chat")
        master.geometry("600x400")
        
        # Główny interfejs
        self.label = Label(master, text="AI Antywirus-Chat", font=("Arial", 16))
        self.label.pack(pady=20)
        
        # Przyciski funkcjonalności
        Button(master, text="Skanuj system", command=self.run_scan).pack(pady=5)
        Button(master, text="Bezpieczne wyszukiwanie", command=self.run_search).pack(pady=5)
        Button(master, text="Chat z AI", command=self.run_ai_chat).pack(pady=5)
        
        # Menu główne
        menubar = Menu(master)
        master.config(menu=menubar)
        
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Skanuj", command=self.run_scan)
        file_menu.add_command(label="Wyszukaj", command=self.run_search)
        file_menu.add_separator()
        file_menu.add_command(label="Wyjdź", command=master.quit)
        menubar.add_cascade(label="Opcje", menu=file_menu)
    
    def run_scan(self):
        scan_files()
        analyze_threats()
        messagebox.showinfo("Skanowanie", "Skanowanie zakończone!")
    
    def run_search(self):
        query = "test"  # Tymczasowo - później dodać pole wprowadzania
        safe_search(query)
    
    def run_ai_chat(self):
        response = generate_response("Witaj, jestem AI Antywirus-Chat")
        messagebox.showinfo("AI Odpowiedź", response)

def init_gui():
    root = Tk()
    app = AntywirusGUI(root)
    root.mainloop()
