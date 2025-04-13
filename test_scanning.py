import unittest
from unittest.mock import patch, MagicMock
from universal_antivirus import UniversalAntivirus
from ml_model import AdvancedMalwareDetector
import os
import time

class TestScanning(unittest.TestCase):
    def setUp(self):
        self.av = UniversalAntivirus()
        self.av.log = MagicMock()
        
        # Mock system manager
        self.av.system_manager = MagicMock()
        self.av.system_manager.system_info = {'system': 'Windows'}
        
        # Mock performance monitor
        self.av.performance_monitor = MagicMock()

    @patch('universal_antivirus.os.walk')
    @patch('universal_antivirus.os.path.getmtime')
    def test_full_scan(self, mock_mtime, mock_walk):
        """Test pełnego skanowania systemu"""
        # Setup mock filesystem
        mock_walk.return_value = [
            ('C:\\Windows', [], ['file1.exe', 'file2.dll']),
            ('C:\\Program Files', [], ['app1.exe', 'data.dat'])
        ]
        mock_mtime.return_value = 0  # Stare pliki
        
        threats = self.av.full_scan()
        
        # Sprawdź czy wywołano logowanie
        self.av.log.assert_any_call("Rozpoczęcie pełnego skanowania systemu...")
        self.av.log.assert_any_call("Pełne skanowanie zakończone.")
        
        # Sprawdź czy zapisano statystyki
        self.av.performance_monitor.record_scan_stats.assert_called_once()

    @patch('universal_antivirus.psutil.process_iter')
    def test_realtime_protection(self, mock_process):
        """Test ochrony czasu rzeczywistego"""
        # Mock procesów
        proc1 = MagicMock()
        proc1.info = {'pid': 1, 'name': 'safe.exe', 'exe': 'C:\\safe.exe', 'create_time': time.time()}
        
        proc2 = MagicMock()
        proc2.info = {'pid': 2, 'name': 'malware.exe', 'exe': 'C:\\malware.exe', 'create_time': time.time()}
        
        mock_process.return_value = [proc1, proc2]
        
        # Mock wykrywania malware
        with patch.object(AdvancedMalwareDetector, 'detect_malware', side_effect=[False, True]):
            self.av.realtime_protection_worker()
            
            # Sprawdź czy wykryto i zakończono złośliwy proces
            proc2.kill.assert_called_once()
            self.av.log.assert_any_call(f"Zakończono podejrzany proces malware.exe (PID: 2)")

    @patch('universal_antivirus.hashlib.sha256')
    def test_malware_detection(self, mock_sha):
        """Test wykrywania malware"""
        # Mock hasha pliku
        mock_sha.return_value.hexdigest.return_value = "a1b2c3"
        
        # Dodaj testową definicję zagrożenia
        self.av.threat_definitions = {
            "trojans": [{"hash": "a1b2c3", "name": "Test.Trojan"}]
        }
        
        detected = self.av.detect_malware("C:\\malware.exe")
        self.assertTrue(detected)
        
        # Test negatywny
        mock_sha.return_value.hexdigest.return_value = "cleanhash"
        detected = self.av.detect_malware("C:\\clean.exe")
        self.assertFalse(detected)

if __name__ == '__main__':
    unittest.main()
