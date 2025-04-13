import unittest
import os
from antivirus_agent_ai import calculate_file_hash, extract_features, is_suspicious
import tempfile

class TestAntivirusFunctions(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.write(b"Test file content")
        self.test_file.close()
        
    def tearDown(self):
        os.unlink(self.test_file.name)
        
    def test_calculate_file_hash(self):
        hash_value = calculate_file_hash(self.test_file.name)
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)  # Długość hash SHA-256
        
    def test_extract_features(self):
        features = extract_features(self.test_file.name)
        self.assertIsInstance(features, list)
        self.assertEqual(len(features), 7)  # Powinno być 7 cech
        
    def test_is_suspicious(self):
        self.assertTrue(is_suspicious("This contains malware"))
        self.assertTrue(is_suspicious("Virus detected"))
        self.assertFalse(is_suspicious("Normal file content"))
        
if __name__ == "__main__":
    unittest.main()
