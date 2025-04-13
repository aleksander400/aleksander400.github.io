import os
import psutil
from datetime import datetime

def scan_file_for_threats(file_path, scan_mode="standard"):
    """Scan individual file for threats with different scan modes"""
    try:
        if not os.path.exists(file_path):
            return "⚠️ Błąd: Plik nie istnieje"
            
        threats = []
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Basic checks for all scan modes
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace').lower()
            
            if "powershell" in content:
                threats.append("Komenda PowerShell")
            if "rm -rf" in content or "del /f /q" in content:
                threats.append("Komenda usuwająca pliki")
            if "eval(" in content or "exec(" in content:
                threats.append("Niebezpieczne funkcje eval/exec")
            if "http://" in content or "https://" in content:
                threats.append("Podejrzane połączenia sieciowe")
        
        # Additional checks for deep scan mode
        if scan_mode == "deep":
            if ext in ['.exe', '.dll', '.bat', '.vbs', '.ps1']:
                threats.append(f"Podejrzany plik wykonywalny ({ext})")
            
            # Check file size anomalies
            file_size = os.path.getsize(file_path)
            if file_size > 10*1024*1024:  # 10MB
                threats.append("Niezwykle duży plik")
            elif file_size == 0:
                threats.append("Pusty plik wykonywalny")
        
        if threats:
            return f"⚠️ Zagrożenia w {filename}:\n- " + "\n- ".join(threats)
        return f"✅ Plik {filename} jest bezpieczny"
    except Exception as e:
        return f"❌ Błąd skanowania: {str(e)}"

def scan_folder_for_threats(folder_path):
    """Scan all files in a folder recursively"""
    try:
        if not os.path.exists(folder_path):
            return "⚠️ Błąd: Folder nie istnieje"
            
        results = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                results.append(f"\n{file_path}:\n{scan_file_for_threats(file_path)}")
                
        return "Wyniki skanowania folderu:" + "\n".join(results)
    except Exception as e:
        return f"❌ Błąd skanowania folderu: {str(e)}"

def scan_running_processes():
    """Check running processes for suspicious activity"""
    try:
        suspicious = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                if "powershell" in cmd or "cmd.exe" in cmd:
                    suspicious.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
            except:
                continue
                
        if suspicious:
            return "⚠️ Podejrzane procesy:\n- " + "\n- ".join(suspicious)
        return "✅ Nie wykryto podejrzanych procesów"
    except Exception as e:
        return f"❌ Błąd skanowania procesów: {str(e)}"

def scan_system():
    """Perform complete system scan and return results"""
    try:
        report = []
        report.append("=== Skanowanie procesów ===")
        report.append(scan_running_processes())
        
        report.append("\n=== Skanowanie bieżącego folderu ===")
        report.append(scan_folder_for_threats("."))
        
        report.append("\n=== Podsumowanie ===")
        report.append(get_last_scan_report())
        
        return "\n".join(report)
    except Exception as e:
        return f"❌ Błąd podczas skanowania systemu: {str(e)}"

def get_last_scan_report():
    """Generate summary of last scan"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Raport skanowania z {timestamp}\nSystem zabezpieczeń aktywny"

# Cache to prevent duplicate scans
_last_scan_time = None
