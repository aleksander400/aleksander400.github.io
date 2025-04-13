from file_analyzer import analyze_file_content
from ml_model import AdvancedMalwareDetector
import os
import hashlib
import datetime

# Inicjalizacja modelu detekcji malware
malware_detector = AdvancedMalwareDetector(model_type='random_forest')

def scan_system():
    """Przeskanuj system w poszukiwaniu zagrożeń"""
    results = []
    suspicious_files = []
    malware_files = []
    
    # Sprawdź główne katalogi systemowe
    system_dirs = [
        os.path.expanduser("~"),
        "C:\\Windows\\Temp",
        "C:\\Windows\\System32",
        "C:\\Program Files",
        "C:\\Program Files (x86)"
    ]
    
    for dir_path in system_dirs:
        if not os.path.exists(dir_path):
            continue
            
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_hash = calculate_file_hash(file_path)
                    file_analysis = analyze_file_content(file_path)
                    
                    # Analiza tradycyjna
                    if is_suspicious(file_analysis):
                        suspicious_files.append({
                            'path': file_path,
                            'hash': file_hash,
                            'analysis': file_analysis,
                            'type': 'suspicious'
                        })
                    
                    # Analiza za pomocą modelu AI
                    features = extract_features(file_path)
                    if features:
                        prediction = malware_detector.predict(features)
                        if prediction == 1:  # malware
                            malware_files.append({
                                'path': file_path,
                                'hash': file_hash,
                                'analysis': "Wykryto przez model AI",
                                'type': 'malware'
                            })
                            
                except Exception as e:
                    continue
                    
    # Generowanie raportu
    if suspicious_files or malware_files:
        results.append("=== Wyniki skanowania ===")
        results.append(f"Data skanowania: {datetime.datetime.now()}")
        
        if malware_files:
            results.append("\n[!] WYKRYTO ZAGROŻENIA (AI):")
            for file in malware_files:
                results.append(f"\nŚcieżka: {file['path']}")
                results.append(f"Hash: {file['hash']}")
                results.append(f"Typ: {file['type'].upper()}")
                results.append(f"Analiza: {file['analysis']}")
                
        if suspicious_files:
            results.append("\n[?] PODEJRZANE PLIKI:")
            for file in suspicious_files:
                results.append(f"\nŚcieżka: {file['path']}")
                results.append(f"Hash: {file['hash']}")
                results.append(f"Typ: {file['type'].upper()}")
                results.append(f"Analiza: {file['analysis']}")
                
        results.append(f"\nPodsumowanie:")
        results.append(f"- Wykryte zagrożenia: {len(malware_files)}")
        results.append(f"- Podejrzane pliki: {len(suspicious_files)}")
    else:
        results.append("Nie znaleziono żadnych zagrożeń")
        
    return "\n".join(results)

def calculate_file_hash(file_path):
    """Oblicz hash SHA-256 pliku"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def is_suspicious(analysis):
    """Określ czy plik jest podejrzany na podstawie analizy"""
    suspicious_keywords = [
        'malware', 'virus', 'trojan', 'worm', 
        'spyware', 'adware', 'ransomware'
    ]
    return any(keyword in analysis.lower() for keyword in suspicious_keywords)

def calculate_entropy(file_path):
    """Oblicz entropię pliku"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            if not data:
                return 0.0
                
            entropy = 0.0
            for x in range(256):
                p_x = float(data.count(x))/len(data)
                if p_x > 0:
                    entropy += - p_x * math.log(p_x, 2)
            return entropy
    except Exception:
        return 0.0

def extract_features(file_path):
    """Wyodrębnij cechy pliku do analizy przez model AI"""
    try:
        file_stats = os.stat(file_path)
        is_executable = os.access(file_path, os.X_OK)
        is_hidden = bool(os.stat(file_path).st_file_attributes & 2)  # FILE_ATTRIBUTE_HIDDEN
        
        features = [
            file_stats.st_size,  # rozmiar pliku
            calculate_entropy(file_path),  # entropia pliku
            int(is_executable),  # flaga wykonywalności
            int(is_hidden),  # flaga ukrytego pliku
            file_stats.st_atime,  # czas ostatniego dostępu
            file_stats.st_mtime,  # czas modyfikacji
            len(file_path.split('\\'))  # głębokość ścieżki
        ]
        return features
    except Exception:
        return None

from tkinter import Tk, Button, Label, Text, messagebox, ttk, filedialog
import logging
from concurrent.futures import ThreadPoolExecutor
import schedule
import time
import shutil
from virus_total_apis import PublicApi as VirusTotalPublicApi
from quarantine_manager import QuarantineManager

qm = QuarantineManager()
from quarantine_manager import QuarantineManager

# Konfiguracja logowania
logging.basicConfig(
    filename="antivirus.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_event(message):
    logging.info(message)

def scan_file(file_path):
    """Skanowanie pojedynczego pliku"""
    try:
        file_hash = calculate_file_hash(file_path)
        file_analysis = analyze_file_content(file_path)
        features = extract_features(file_path)
        
        result = {
            'path': file_path,
            'hash': file_hash,
            'analysis': file_analysis,
            'type': 'safe'
        }
        
        if features:
            prediction = malware_detector.predict(features)
            if prediction == 1:
                result['type'] = 'malware'
                result['analysis'] = "Wykryto przez model AI"
        return result
    except Exception as e:
        log_event(f"Błąd podczas skanowania {file_path}: {str(e)}")
        return None

def scan_directory_parallel(dir_path):
    """Skanowanie katalogu z wykorzystaniem wielowątkowości"""
    results = []
    with ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(dir_path):
            futures = [executor.submit(scan_file, os.path.join(root, file)) for file in files]
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)
    return results

def gui_app():
    """Interfejs graficzny aplikacji"""
    root = Tk()
    root.title("Antivirus Agent AI - Professional Edition")
    root.geometry("1000x800")
    
    # Konfiguracja API VirusTotal
    VT_API_KEY = "YOUR_API_KEY"  # Należy zastąpić prawdziwym kluczem
    vt_api = VirusTotalPublicApi(VT_API_KEY) if VT_API_KEY != "YOUR_API_KEY" else None
    qm = QuarantineManager()
    
    def check_virustotal(file_hash):
        """Sprawdź plik w VirusTotal"""
        if not vt_api:
            return "Brak konfiguracji VirusTotal API"
        try:
            response = vt_api.get_file_report(file_hash)
            if response['response_code'] == 200:
                return f"Wynik VirusTotal: {response['results']['positives']}/{response['results']['total']}"
            return "Brak danych w VirusTotal"
        except Exception as e:
            return f"Błąd VirusTotal: {str(e)}"

    # Nagłówek
    Label(root, text="Antivirus Agent AI", font=("Arial", 16)).pack(pady=10)

    # Przyciski akcji
    def start_scan():
        log_event("Rozpoczęto skanowanie systemu")
        text_area.delete("1.0", "end")
        text_area.insert("end", "Trwa skanowanie... Proszę czekać.\n")
        root.update()
        
        try:
            system_dirs = [
                os.path.expanduser("~"),
                "C:\\Windows\\Temp",
                "C:\\Windows\\System32",
                "C:\\Program Files",
                "C:\\Program Files (x86)"
            ]
            
            results = []
            for dir_path in system_dirs:
                if os.path.exists(dir_path):
                    results.extend(scan_directory_parallel(dir_path))
            
            malware_count = sum(1 for r in results if r['type'] == 'malware')
            suspicious_count = sum(1 for r in results if r['type'] == 'suspicious')
            
            text_area.delete("1.0", "end")
            text_area.insert("end", f"=== Wyniki skanowania ===\n")
            text_area.insert("end", f"Data: {datetime.datetime.now()}\n")
            text_area.insert("end", f"Przeskanowane pliki: {len(results)}\n")
            text_area.insert("end", f"Wykryte zagrożenia: {malware_count}\n")
            text_area.insert("end", f"Podejrzane pliki: {suspicious_count}\n\n")
            
            for result in results:
                if result['type'] in ['malware', 'suspicious']:
                    text_area.insert("end", f"Ścieżka: {result['path']}\n")
                    text_area.insert("end", f"Typ: {result['type'].upper()}\n")
                    text_area.insert("end", f"Analiza: {result['analysis']}\n\n")
            
            log_event(f"Zakończono skanowanie. Wykryto {malware_count} zagrożeń.")
            messagebox.showinfo("Sukces", "Skanowanie zakończone pomyślnie!")
        except Exception as e:
            log_event(f"Błąd podczas skanowania: {str(e)}")
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")

    # Panel przycisków
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)
    
    ttk.Button(button_frame, text="Rozpocznij skanowanie", command=start_scan).pack(side="left", padx=5)
    
    def select_directory():
        dir_path = filedialog.askdirectory()
        if dir_path:
            results = scan_directory_parallel(dir_path)
            display_results(results)
    
    ttk.Button(button_frame, text="Wybierz folder", command=select_directory).pack(side="left", padx=5)
    
    def select_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            result = scan_file(file_path)
            display_results([result] if result else [])
    
    ttk.Button(button_frame, text="Sprawdź plik", command=select_file).pack(side="left", padx=5)
    
    def display_results(results):
        text_area.delete("1.0", "end")
        if not results:
            text_area.insert("end", "Brak wyników do wyświetlenia\n")
            return
            
        # Rozbudowane menu kontekstowe
        popup_menu = Menu(root, tearoff=0)
        popup_menu.add_command(label="Przywróć z kwarantanny", 
                             command=lambda: restore_from_quarantine(selected_file))
        popup_menu.add_command(label="Eksportuj raport", 
                             command=lambda: export_report(results))
        popup_menu.add_separator()
        popup_menu.add_command(label="Sprawdź w VirusTotal", 
                             command=lambda: check_virustotal(selected_hash))
        
        def show_popup(event):
            nonlocal selected_file
            try:
                index = text_area.index(f"@{event.x},{event.y}")
                line = text_area.get(f"{index} linestart", f"{index} lineend")
                if "Ścieżka:" in line:
                    selected_file = line.split("Ścieżka:")[1].strip()
                    popup_menu.tk_popup(event.x_root, event.y_root)
            finally:
                popup_menu.grab_release()
                
        text_area.bind("<Button-3>", show_popup)
        selected_file = None
            
        malware_count = sum(1 for r in results if r['type'] == 'malware')
        suspicious_count = sum(1 for r in results if r['type'] == 'suspicious')
        
        text_area.insert("end", f"=== Wyniki skanowania ===\n")
        text_area.insert("end", f"Data: {datetime.datetime.now()}\n")
        text_area.insert("end", f"Przeskanowane pliki: {len(results)}\n")
        text_area.insert("end", f"Wykryte zagrożenia: {malware_count}\n")
        text_area.insert("end", f"Podejrzane pliki: {suspicious_count}\n\n")
        
        for result in results:
            if result['type'] in ['malware', 'suspicious']:
                text_area.insert("end", f"Ścieżka: {result['path']}\n")
                text_area.insert("end", f"Typ: {result['type'].upper()}\n")
                text_area.insert("end", f"Analiza: {result['analysis']}\n\n")

    # Obszar tekstowy na wyniki
    text_area = Text(root, wrap="word", height=30, width=100)
    text_area.pack(pady=10, padx=10)

    root.mainloop()

if __name__ == "__main__":
    gui_app()
