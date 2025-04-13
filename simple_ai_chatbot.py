import os
import psutil
import smtplib
from universal_antivirus import UniversalAntivirus

class AIChatbot:
    def __init__(self):
        self.antivirus = UniversalAntivirus()
        
    def handle_input(self, input_text: str) -> str:
        input_text = input_text.lower()
        
        if "zeskanuj system" in input_text:
            return self.scan_system()
        elif "wyślij e-mail" in input_text:
            return "Podaj szczegóły e-maila (adres, temat, treść)"
        elif "sprawdź procesy" in input_text:
            return self.show_processes()
        else:
            return "Nie rozumiem tego polecenia. Spróbuj jeszcze raz."
    
    def scan_system(self) -> str:
        """Wykonuje skanowanie antywirusowe"""
        result = self.antivirus.detect_malware(use_ml=True)
        if result['is_malware']:
            return f"Znaleziono zagrożenie: {result['threat_name']}"
        return "Skanowanie zakończone - brak zagrożeń"
    
    def show_processes(self) -> str:
        """Pokazuje aktywne procesy systemowe"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            processes.append(f"{proc.info['name']} (PID: {proc.info['pid']}) - CPU: {proc.info['cpu_percent']}%")
        
        top_processes = "\n".join(processes[:5])  # Pokazuje tylko 5 pierwszych
        return f"Aktywne procesy:\n{top_processes}\n[...]"
    
    def send_email(self, address: str, subject: str, body: str) -> str:
        """Wysyła e-mail (funkcja do implementacji)"""
        try:
            # Tutaj implementacja wysyłania emaila
            return f"E-mail do {address} został wysłany"
        except Exception as e:
            return f"Błąd podczas wysyłania e-maila: {str(e)}"

if __name__ == "__main__":
    chatbot = AIChatbot()
    while True:
        user_input = input("Ty: ")
        if user_input.lower() == "wyjście":
            break
        print("AI:", chatbot.handle_input(user_input))
