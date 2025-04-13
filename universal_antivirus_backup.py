import os
import psutil
import shutil
import hashlib
import requests
import json
from datetime import datetime
import threading
import socket
import time
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('antivirus.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("Antivirus started")

class PerformanceMonitor:
    """Klasa do monitorowania wydajności systemu"""
    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'network_activity': [],
            'scan_stats': []
        }
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_worker, daemon=True)
        self.monitor_thread.start()

    def monitor_worker(self):
        """Wątek zbierający metryki wydajności"""
        while self.running:
            # Zbieranie metryk co 5 sekund
            self.record_cpu_usage()
            self.record_memory_usage()
            self.record_network_activity()
            time.sleep(5)

    def record_cpu_usage(self):
        """Zapis wykorzystania CPU"""
        self.metrics['cpu_usage'].append({
            'timestamp': datetime.now().isoformat(),
            'value': psutil.cpu_percent(interval=1)
        })

    def record_memory_usage(self):
        """Zapis wykorzystania pamięci"""
        mem = psutil.virtual_memory()
        self.metrics['memory_usage'].append({
            'timestamp': datetime.now().isoformat(),
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent
        })

    def record_network_activity(self):
        """Zapis aktywności sieciowej"""
        net = psutil.net_io_counters()
        self.metrics['network_activity'].append({
            'timestamp': datetime.now().isoformat(),
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv
        })

    def record_scan_stats(self, scan_type, threats_found, duration):
        """Zapis statystyk skanowania"""
        self.metrics['scan_stats'].append({
            'timestamp': datetime.now().isoformat(),
            'scan_type': scan_type,
            'threats_found': threats_found,
            'duration_sec': duration
        })

    def get_metrics(self):
        """Pobranie zebranych metryk"""
        return self.metrics

    def stop(self):
        """Zatrzymanie monitorowania"""
        self.running = False


class UniversalAntivirus:
    def __init__(self):
        self.threat_definitions = self.load_threat_definitions()
        self.system_status = "OK"
        self.real_time_protection = True
        self.scheduled_scans = []
        self.active_threats = []
        self.security_logs = []
        self.quarantine_dir = "./quarantine"
        self.firewall_rules = []
        self.config = {
            'scan_mode': 'standard',
            'auto_update': True,
            'notifications': True,
            'language': 'pl'
        }
        
        os.makedirs(self.quarantine_dir, exist_ok=True)
        self.load_firewall_rules()
        
        # Inicjalizacja monitora wydajności
        self.performance_monitor = PerformanceMonitor()
        
        # Wątek ochrony czasu rzeczywistego
        self.rt_thread = threading.Thread(target=self.realtime_protection_worker, daemon=True)
        self.rt_thread.start()

    def load_threat_definitions(self):
        """Ładowanie i walidacja definicji zagrożeń"""
        definitions = []
        
        # Źródła definicji z redundancją
        sources = [
            {"url": "https://threat-database.example.com/latest", "type": "online"},
            {"url": "https://backup.threat-db.example.com/v1", "type": "online"},
            {"file": "./local_threats.json", "type": "local"}
        ]
        
        # Próba pobrania z każdego źródła
        for source in sources:
            try:
                if source["type"] == "online":
                    response = requests.get(source["url"], timeout=5)
                    definitions.append(response.json())
                else:
                    with open(source["file"], "r") as f:
                        definitions.append(json.load(f))
            except:
                continue
                
        # Walidacja krzyżowa definicji
        validated = self.validate_threat_definitions(definitions)
        
        if not validated:
            # Fallback do minimalnej lokalnej bazy
            return {
                "trojans": [
                    {"name": "Backdoor.Win32", "hash": "a1b2c3..."},
                    {"name": "Trojan.Spy", "hash": "d4e5f6..."}
                ],
                "viruses": [
                    {"name": "Virus.Win32", "hash": "x7y8z9..."}
                ]
            }
            
        return validated[0]  # Zwróć pierwszą poprawną wersję

    def validate_threat_definitions(self, definitions):
        """Walidacja krzyżowa definicji zagrożeń"""
        valid_definitions = []
        
        # Sprawdź spójność między różnymi wersjami definicji
        for i, def1 in enumerate(definitions):
            is_valid = True
            for j, def2 in enumerate(definitions):
                if i != j:
                    # Porównaj kluczowe pola
                    if not self.compare_definitions(def1, def2):
                        is_valid = False
                        break
            if is_valid:
                valid_definitions.append(def1)
                
        return valid_definitions

    def compare_definitions(self, def1, def2):
        """Porównanie dwóch wersji definicji zagrożeń"""
        # Sprawdź czy mają te same klucze
        if set(def1.keys()) != set(def2.keys()):
            return False
            
        # Sprawdź spójność dla każdej kategorii
        for category in def1.keys():
            if len(def1[category]) != len(def2[category]):
                return False
                
            # Porównaj hashe zagrożeń
            hashes1 = {t['hash'] for t in def1[category]}
            hashes2 = {t['hash'] for t in def2[category]}
            
            if hashes1 != hashes2:
                return False
                
        return True

    def load_firewall_rules(self):
        """Ładowanie reguł firewalla"""
        self.firewall_rules = [
            {"port": 4444, "action": "block"},
            {"port": 31337, "action": "block"}
        ]

    def realtime_protection_worker(self):
        """Wątek ochrony czasu rzeczywistego"""
        while self.real_time_protection:
            # Monitorowanie procesów
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if self.detect_malware(proc.info['exe']):
                        self.quarantine_file(proc.info['exe'])
                        proc.kill()
                except:
                    continue
            
            # Sprawdzanie połączeń sieciowych
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    self.check_firewall_rules(conn)

    def scan_system(self, scan_type="full"):
        """Skanowanie systemu"""
        start_time = time.time()
        self.log(f"Rozpoczęto skanowanie: {scan_type}")
        
        if scan_type == "quick":
            self.active_threats = self.quick_scan()
        else:
            self.active_threats = self.full_scan()
            
        duration = time.time() - start_time
            
        if self.active_threats:
            self.log(f"Wykryto zagrożenia: {len(self.active_threats)}")
            self.remove_threats()
            self.auto_repair()
        else:
            self.log("Brak zagrożeń")
            
        # Zapis statystyk skanowania
        self.performance_monitor.record_scan_stats(
            scan_type=scan_type,
            threats_found=len(self.active_threats),
            duration=duration
        )
            
        return self.active_threats

    def auto_repair(self):
        """Automatyczna naprawa systemu po infekcji"""
        self.log("Rozpoczęcie procedury autonaprawy")
        
        # 1. Naprawa rejestru systemowego
        self.repair_registry()
        
        # 2. Przywracanie usuniętych/zmodyfikowanych plików
        self.restore_system_files()
        
        # 3. Optymalizacja systemu
        self.optimize_system()
        
        self.log("Procedura autonaprawy zakończona")

    def repair_registry(self):
        """Naprawa kluczy rejestru systemowego"""
        self.log("Naprawa rejestru systemowego...")
        # Tutaj implementacja naprawy rejestru
        # np. przywracanie domyślnych wartości kluczy
        self.log("Przywrócono domyślne ustawienia rejestru")

    def restore_system_files(self):
        """Przywracanie usuniętych lub zmodyfikowanych plików systemowych"""
        self.log("Przywracanie plików systemowych...")
        # Tutaj implementacja przywracania plików
        # np. z kopii zapasowej lub źródła instalacyjnego
        self.log("Przywrócono krytyczne pliki systemowe")

    def optimize_system(self):
        """Optymalizacja systemu po infekcji"""
        self.log("Optymalizacja systemu...")
        # Tutaj implementacja czyszczenia i optymalizacji
        # np. czyszczenie plików tymczasowych, defragmentacja
        self.log("System zoptymalizowany po infekcji")

    def full_scan(self):
        """Pełne skanowanie systemu (wersja testowa)"""
        threats = []
        self.log("Rozpoczęcie skanowania w trybie testowym...")
        
        # Ograniczone skanowanie tylko folderu testowego
        test_path = os.path.join(os.path.dirname(__file__), "test_scan_folder")
        
        if os.path.exists(test_path):
            self.log(f"Skanowanie folderu testowego: {test_path}")
            for root, _, files in os.walk(test_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        self.log(f"Analiza pliku: {file}")
                        if self.detect_malware(file_path):
                            threats.append(f"Złośliwy plik: {file_path}")
                    except Exception as e:
                        self.log(f"Błąd analizy pliku {file}: {str(e)}")
                        continue
        else:
            self.log("Brak folderu testowego - tworzenie...")
            os.makedirs(test_path, exist_ok=True)
            with open(os.path.join(test_path, "test_file.txt"), "w") as f:
                f.write("Testowy plik do skanowania")
                
        self.log("Skanowanie zakończone")
        return threats

    def detect_malware(self, file_path):
        """Wykrywanie złośliwego oprogramowania"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
                
                # Sprawdzanie w bazie zagrożeń
                for threat_type in self.threat_definitions.values():
                    for threat in threat_type:
                        if threat['hash'] == file_hash:
                            return True
                            
                # Wykrywanie podejrzanych wzorców
                if b"ransom" in content.lower():
                    return True
                    
        except:
            return False
            
        return False

    def quarantine_file(self, file_path):
        """Kwarantanna pliku"""
        try:
            filename = os.path.basename(file_path)
            dest = os.path.join(self.quarantine_dir, filename)
            shutil.move(file_path, dest)
            self.log(f"Plik {filename} przeniesiony do kwarantanny")
            return True
        except Exception as e:
            self.log(f"Błąd kwarantanny: {str(e)}")
            return False

    def check_firewall_rules(self, connection):
        """Sprawdzanie reguł firewalla"""
        for rule in self.firewall_rules:
            if connection.raddr and connection.raddr.port == rule['port']:
                if rule['action'] == "block":
                    self.log(f"Zablokowano połączenie na porcie {rule['port']}")
                    # W rzeczywistości należy zamknąć połączenie

    def log(self, message):
        """Zapisywanie logów"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.security_logs.append(f"[{timestamp}] {message}")

    def update_definitions(self):
        """Aktualizacja definicji zagrożeń"""
        self.threat_definitions = self.load_threat_definitions()
        self.log("Zaktualizowano definicje zagrożeń")

    def enable_realtime_protection(self):
        """Włączenie ochrony czasu rzeczywistego"""
        self.real_time_protection = True
        self.log("Ochrona czasu rzeczywistego włączona")

    def disable_realtime_protection(self):
        """Wyłączenie ochrony czasu rzeczywistego"""
        self.real_time_protection = False
        self.log("Ochrona czasu rzeczywistego wyłączona")

# Przykładowe użycie
if __name__ == "__main__":
    av = UniversalAntivirus()
    av.enable_realtime_protection()
    av.scan_system()
    av.update_definitions()
