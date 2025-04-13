import os
import psutil
from datetime import datetime

def scan_file_for_threats(file_path, scan_mode="standard"):
    """Enhanced file scanning with multiple modes"""
    try:
        if not os.path.exists(file_path):
            return "⚠️ Błąd: Plik nie istnieje"
            
        threats = []
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Basic checks
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace').lower()
            
            if "powershell" in content:
                threats.append("Komenda PowerShell")
            if "rm -rf" in content or "del /f /q" in content:
                threats.append("Komenda usuwająca pliki")
            if "eval(" in content or "exec(" in content:
                threats.append("Niebezpieczne funkcje eval/exec")
        
        # Deep scan checks        
        if scan_mode == "deep":
            if ext in ['.exe', '.dll', '.bat', '.vbs', '.ps1']:
                threats.append(f"Podejrzany plik wykonywalny ({ext})")
                
        if threats:
            return f"⚠️ Zagrożenia w {filename}:\n- " + "\n- ".join(threats)
        return f"✅ Plik {filename} jest bezpieczny"
    except Exception as e:
        return f"❌ Błąd skanowania: {str(e)}"

def scan_system(mode="standard"):
    """Enhanced system scanning with modes"""
    try:
        report = []
        report.append(f"=== Rozpoczęto skanowanie w trybie {mode} ===")
        
        # File scanning based on mode
        if mode == "quick":
            report.append("Skanowanie szybkie (50 plików)")
        elif mode == "deep":
            report.append("Skanowanie głębokie")
        else:
            report.append("Skanowanie standardowe")
            
        return "\n".join(report)
    except Exception as e:
        return f"❌ Błąd skanowania: {str(e)}"
