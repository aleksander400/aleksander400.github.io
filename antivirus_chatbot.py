from universal_antivirus import UniversalAntivirus
from system_agent import SystemManager
import logging
import psutil

# Konfiguracja logowania
logging.basicConfig(
    filename='antivirus_chatbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

system_manager = SystemManager()

class AntivirusChatbot:
    def __init__(self):
        self.qa_pairs = {
            "jak się masz": "Dobrze, dzięki że pytasz.",
            "kim jesteś": "Jestem Nova - Twoja cyberpunkowa asystentka antywirusowa",
            "co potrafisz": "Potrafię skanować system, monitorować procesy i wykrywać zagrożenia"
        }

    def scan_system(self, scan_type='quick'):
        """Zaawansowane skanowanie systemu"""
        try:
            logging.info(f"Rozpoczęto skanowanie systemu (typ: {scan_type})")
            antivirus = UniversalAntivirus()
            if scan_type == 'quick':
                result = antivirus.scan_system("quick")
            else:
                result = antivirus.scan_system("full")
            logging.info("Skanowanie zakończone pomyślnie")
            return result
        except Exception as e:
            logging.error(f"Błąd podczas skanowania: {str(e)}")
            return f"Błąd skanowania: {str(e)}"

    def check_processes(self, filter_suspicious=False):
        """Monitorowanie aktywnych procesów"""
        try:
            processes = system_manager.list_processes()
            if filter_suspicious:
                processes = [p for p in processes if p['cpu_percent'] > 50 or p['memory_percent'] > 5]
            
            process_list = "\n".join(
                f"{p['name']} (PID: {p['pid']}, CPU: {p['cpu_percent']}%, RAM: {p['memory_percent']}%)" 
                for p in processes[:10]
            )
            return f"Aktywne procesy:\n{process_list}"
        except Exception as e:
            logging.error(f"Błąd sprawdzania procesów: {str(e)}")
            return f"Błąd: {str(e)}"

    def handle_command(self, input_text):
        """Obsługa komend użytkownika"""
        if not input_text.strip():
            return "Nie podałeś żadnego polecenia."
        
        input_text = input_text.lower()
        try:
            # Sprawdź podstawowe pytania
            for question, answer in self.qa_pairs.items():
                if question in input_text:
                    return answer

            # Obsługa komend systemowych
            if "zeskanuj system" in input_text:
                if "pełne" in input_text:
                    return self.scan_system(scan_type='full')
                return self.scan_system()
                
            elif "sprawdź procesy" in input_text:
                if "podejrzane" in input_text:
                    return self.check_processes(filter_suspicious=True)
                return self.check_processes()
                
            else:
                return "Nie rozumiem polecenia. Dostępne komendy: 'zeskanuj system', 'sprawdź procesy'"
                
        except Exception as e:
            logging.error(f"Błąd przetwarzania komendy: {str(e)}")
            return f"Wystąpił błąd: {str(e)}"

# Przykład użycia
if __name__ == "__main__":
    chatbot = AntivirusChatbot()
    print(chatbot.handle_command("zeskanuj system"))
    print(chatbot.handle_command("sprawdź procesy"))
    print(chatbot.handle_command("kim jesteś"))
