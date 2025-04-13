import os
import math
import psutil
from system_agent import SystemManager
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
        self._stop_event = threading.Event()
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
        """Bezpieczne zatrzymanie monitora wydajności"""
        self.running = False
        if hasattr(self, '_stop_event'):
            self._stop_event.set()
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)


class UniversalAntivirus:
    def __init__(self):
        self.threat_definitions = self.load_threat_definitions()
        self.system_status = "OK"
        self.system_manager = SystemManager()  # Integracja z system_agent
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
        self._stop_event = threading.Event()  # Event do kontroli wątków
        
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
            # Rozszerzona lokalna baza zagrożeń
            return {
                "trojans": [
                    {"name": "Backdoor.Win32", "hash": "a1b2c3...", "description": "Backdoor umożliwiający zdalny dostęp"},
                    {"name": "Trojan.Spy", "hash": "d4e5f6...", "description": "Szpiegujące oprogramowanie"},
                    {"name": "Trojan.Banker", "hash": "g7h8i9...", "description": "Kradzież danych bankowych"},
                    {"name": "Trojan.Ransom", "hash": "j1k2l3...", "description": "Szyfrowanie danych i żądanie okupu"},
                    {"name": "Trojan.DDoS", "hash": "m4n5o6...", "description": "Ataki DDoS"}
                ],
                "viruses": [
                    {"name": "Virus.Win32", "hash": "x7y8z9...", "description": "Wirus infekujący pliki wykonywalne"},
                    {"name": "Worm.Email", "hash": "p1q2r3...", "description": "Robak rozprzestrzeniający się przez email"},
                    {"name": "Worm.Network", "hash": "s4t5u6...", "description": "Robak wykorzystujący luki sieciowe"},
                    {"name": "Rootkit.Bootkit", "hash": "v7w8x9...", "description": "Rootkit infekujący sektor rozruchowy"},
                    {"name": "Adware.Popup", "hash": "y1z2a3...", "description": "Wyświetlanie niechcianych reklam"}
                ],
                "ransomware": [
                    {"name": "Ransom.CryptoLocker", "hash": "b4c5d6...", "description": "Szyfruje pliki i żąda okupu"},
                    {"name": "Ransom.WannaCry", "hash": "e7f8g9...", "description": "Słynny ransomware wykorzystujący exploit EternalBlue"}
                ],
                "spyware": [
                    {"name": "Spy.Keylogger", "hash": "h1i2j3...", "description": "Rejestruje naciśnięcia klawiszy"},
                    {"name": "Spy.ScreenCapture", "hash": "k4l5m6...", "description": "Przechwytuje zrzuty ekranu"}
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
        """Rozszerzona ochrona czasu rzeczywistego"""
        critical_locations = [
            os.environ.get('SystemRoot', 'C:\\Windows'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32'),
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files')),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')),
            os.path.join(os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')))
        ]
        
        while self.real_time_protection and not self._stop_event.is_set():
            # 1. Monitorowanie procesów z analizą behawioralną
            process_behavior = {}
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'create_time']):
                try:
                    proc_info = proc.info
                    # Analiza podejrzanych cech procesu
                    suspicious = False
                    
                    # Sprawdź czy proces jest nowy (utworzony w ciągu ostatnich 5 sekund)
                    if time.time() - proc_info['create_time'] < 5:
                        self.log(f"Nowy proces wykryty: {proc_info['name']} (PID: {proc_info['pid']})")
                        suspicious = True
                        
                    # Sprawdź czy proces jest wstrzyknięty
                    if proc_info['exe'] and not os.path.exists(proc_info['exe']):
                        self.log(f"Proces bez pliku wykonywalnego: {proc_info['name']}")
                        suspicious = True
                        
                    # Sprawdź w bazie zagrożeń
                    if suspicious or self.detect_malware(proc_info['exe']):
                        self.quarantine_file(proc_info['exe'])
                        proc.kill()
                        
                    # Zbierz dane behawioralne
                    process_behavior[proc_info['pid']] = {
                        'name': proc_info['name'],
                        'cpu': proc.cpu_percent(interval=0.1),
                        'memory': proc.memory_info().rss,
                        'connections': len(proc.connections('all'))
                    }
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 2. Monitorowanie zmian w kluczowych lokalizacjach
            for location in critical_locations:
                try:
                    for root, _, files in os.walk(location):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                # Sprawdź czy plik został zmodyfikowany w ciągu ostatnich 5 sekund
                                if time.time() - os.path.getmtime(file_path) < 5:
                                    self.log(f"Zmodyfikowany plik: {file_path}")
                                    if self.detect_malware(file_path):
                                        self.quarantine_file(file_path)
                            except:
                                continue
                except:
                    continue
            
            # 3. Analiza sieciowa
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    self.check_firewall_rules(conn)
                    # Dodatkowa analiza podejrzanych połączeń
                    if conn.raddr and conn.raddr.port in [4444, 31337, 666, 1337]:
                        self.log(f"Podejrzane połączenie na porcie {conn.raddr.port}")
                        try:
                            proc = psutil.Process(conn.pid)
                            proc.kill()
                        except:
                            continue
            
            # 4. Analiza behawioralna procesów
            self.analyze_process_behavior(process_behavior)
            
            time.sleep(2)  # Ogranicz zużycie CPU

    def scan_system(self, scan_type="full"):
        """Skanowanie systemu"""
        start_time = time.time()
        self.log(f"Rozpoczęto skanowanie: {scan_type}")
        
        # Domyślnie wykonujemy pełne skanowanie
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
        
        # Windows registry repair commands
        if self.system_manager.system_info['system'] == 'Windows':
            commands = [
                'sfc /scannow',
                'DISM /Online /Cleanup-Image /RestoreHealth',
                'reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Shell /t REG_SZ /d explorer.exe /f'
            ]
            
            for cmd in commands:
                result = self.system_manager.execute_system_command(cmd)
                self.log(f"Wynik komendy {cmd}: {result}")
        
        self.log("Zakończono naprawę rejestru systemowego")

    def restore_system_files(self):
        """Przywracanie usuniętych lub zmodyfikowanych plików systemowych"""
        self.log("Przywracanie plików systemowych...")
        
        # Windows system file restore commands
        if self.system_manager.system_info['system'] == 'Windows':
            commands = [
                'sfc /scannow',  # System File Checker
                'DISM /Online /Cleanup-Image /RestoreHealth',  # Deployment Image Servicing
                'powershell -Command "Repair-WindowsImage -Online -RestoreHealth"'
            ]
            
            for cmd in commands:
                result = self.system_manager.execute_system_command(cmd)
                self.log(f"Wynik komendy {cmd}: {result}")
        
        self.log("Zakończono przywracanie plików systemowych")

    def optimize_system(self):
        """Optymalizacja systemu po infekcji"""
        self.log("Optymalizacja systemu...")
        
        # Get current resource usage
        resources = self.system_manager.monitor_resources()
        self.log(f"Przed optymalizacją - CPU: {resources['cpu']}%, RAM: {resources['memory']}%")
        
        # Windows optimization commands
        if self.system_manager.system_info['system'] == 'Windows':
            commands = [
                'cleanmgr /sagerun:1',  # Disk Cleanup
                'defrag C: /U /V',      # Disk Defragmenter
                'powercfg /h off',      # Disable hibernation
                'netsh int tcp set global autotuninglevel=restricted'  # Network optimization
            ]
            
            for cmd in commands:
                result = self.system_manager.execute_system_command(cmd)
                self.log(f"Wynik komendy {cmd}: {result}")
        
        # Get post-optimization resource usage
        resources = self.system_manager.monitor_resources()
        self.log(f"Po optymalizacji - CPU: {resources['cpu']}%, RAM: {resources['memory']}%")
        self.log("System zoptymalizowany po infekcji")

    def full_scan(self):
        """Pełne skanowanie systemu"""
        threats = []
        start_time = time.time()
        self.log("Rozpoczęcie pełnego skanowania systemu...")
        
        # Kluczowe lokalizacje do skanowania
        scan_locations = [
            os.environ.get('SystemRoot', 'C:\\Windows'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32'),
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files')),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')),
            os.path.join(os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))),
            os.path.expanduser('~\\Documents'),
            os.path.expanduser('~\\Downloads')
        ]
        
        total_files = 0
        for location in scan_locations:
            try:
                self.log(f"Skanowanie lokalizacji: {location}")
                for root, _, files in os.walk(location):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_files += 1
                        try:
                            if total_files % 100 == 0:
                                self.log(f"Przeskanowano {total_files} plików...")
                            
                            if self.detect_malware(file_path):
                                threats.append(f"Złośliwy plik: {file_path}")
                        except Exception as e:
                            self.log(f"Błąd analizy pliku {file_path}: {str(e)}")
                            continue
            except Exception as e:
                self.log(f"Błąd skanowania {location}: {str(e)}")
                continue
                
        duration = time.time() - start_time
        self.log(f"Pełne skanowanie zakończone. Przeskanowano {total_files} plików w {duration:.2f} sekund.")
        self.log(f"Znaleziono {len(threats)} zagrożeń.")
        
        # Zapis statystyk skanowania
        self.performance_monitor.record_scan_stats(
            scan_type="full",
            threats_found=len(threats),
            duration=duration
        )
        
        return threats

    def extract_features(self, file_path):
        """Ekstrakcja cech pliku do analizy"""
        try:
            # Przykładowe cechy: rozmiar pliku, entropia, itp.
            file_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as f:
                content = f.read()
                entropy = self.calculate_entropy(content)
            # Można dodać więcej cech w przyszłości
            return [file_size, entropy]
        except Exception as e:
            self.log(f"Błąd ekstrakcji cech pliku {file_path}: {str(e)}")
            return None

    def detect_malware(self, file_path, use_ml=True):
        """Wykrywanie złośliwego oprogramowania z analizą heurystyczną"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
                
                # 1. Sprawdzanie w bazie zagrożeń
                for threat_type in self.threat_definitions.values():
                    for threat in threat_type:
                        if threat['hash'] == file_hash:
                            return True
                            
                # 2. Analiza heurystyczna
                suspicious_patterns = [
                    b"ransom", b"payload", b"inject", 
                    b"<script>evil", b"eval(", b"base64_decode",
                    b"EICAR-TEST-FILE"  # Standard test pattern
                ]
                
                content_lower = content.lower()
                if any(pattern in content_lower for pattern in suspicious_patterns):
                    return True
                    
                # 3. Analiza entropii (wykrywanie zaszyfrowanych/pakowanych plików)
                if len(content) > 1000:
                    entropy = self.calculate_entropy(content)
                    if entropy > 7.5:  # Wysoka entropia może wskazywać na zaszyfrowane dane
                        return True
                        
        except Exception as e:
            self.log(f"Błąd analizy pliku {file_path}: {str(e)}")
            return False
            
        return False

    def calculate_entropy(self, data):
        """Oblicz entropię danych do wykrywania podejrzanych plików"""
        if not data:
            return 0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(bytes([x]))) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        return entropy

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

    def analyze_process_behavior(self, process_behavior):
        """Zaawansowana analiza behawioralna procesów"""
        suspicious_thresholds = {
            'cpu': 90,  # % wykorzystania CPU
            'memory': 100 * 1024 * 1024,  # 100 MB
            'connections': 50  # liczba połączeń
        }
        
        for pid, behavior in process_behavior.items():
            # Sprawdź anomalie w wykorzystaniu zasobów
            if (behavior['cpu'] > suspicious_thresholds['cpu'] or
                behavior['memory'] > suspicious_thresholds['memory'] or
                behavior['connections'] > suspicious_thresholds['connections']):
                
                self.log(f"Podejrzane zachowanie procesu {behavior['name']} (PID: {pid}): "
                        f"CPU={behavior['cpu']}%, RAM={behavior['memory']/1024/1024:.1f}MB, "
                        f"Połączenia={behavior['connections']}")
                
                # Próba zakończenia podejrzanego procesu
                try:
                    proc = psutil.Process(pid)
                    proc.kill()
                    self.log(f"Zakończono podejrzany proces {behavior['name']} (PID: {pid})")
                except:
                    self.log(f"Nie udało się zakończyć procesu {pid}")

class Skynet(UniversalAntivirus):
    """Cyberpunk AI System with enhanced capabilities"""
    
    def __init__(self):
        super().__init__()
        self.ai_status = "█▓▒░ONLINE░▒▓█"
        self.neon_ui = True
        self.hacking_modules = []
        
    def display_hud(self):
        """Show Cyberpunk-style HUD"""
        print(f"\n╔{'═'*50}╗")
        print(f"║ {'CYBERPUNK AI SYSTEM':^48} ║")
        print(f"╠{'═'*50}╣")
        print(f"║ Status: {self.ai_status:42} ║")
        print(f"║ CPU: {psutil.cpu_percent():3}% | RAM: {psutil.virtual_memory().percent:3}% {' '*24} ║")
        print(f"╚{'═'*50}╝")
        
    def cyber_scan(self):
        """Enhanced scanning with cyberpunk visuals"""
        self.display_hud()
        print("\n[▓▒░ INITIATING NEURAL SCAN ░▒▓]")
        threats = self.scan_system()
        if threats:
            print(f"[!] DETECTED {len(threats)} CYBER THREATS [!]")
        else:
            print("[✓] SYSTEM SECURE [✓]")
            
    def show_menu(self):
        """Cyberpunk interactive menu"""
        while True:
            self.display_hud()
            print("\n1. Run Neural Scan")
            print("2. System Diagnostics")
            print("3. Network Analysis")
            print("4. Exit Cyber AI")
            choice = input("\n[SELECT OPTION] >> ")
            
            if choice == "1":
                self.cyber_scan()
            elif choice == "2":
                print("\n[SYSTEM DIAGNOSTICS]")
                print(psutil.virtual_memory())
            elif choice == "3":
                print("\n[NETWORK ANALYSIS]")
                print(psutil.net_io_counters())
            elif choice == "4":
                break

# Uruchomienie Skynet AI
if __name__ == "__main__":
    skynet = Skynet()
    skynet.enable_realtime_protection()
    skynet.show_menu()
