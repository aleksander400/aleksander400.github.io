import unittest
import time
from universal_antivirus import PerformanceMonitor

class TestPerformanceMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = PerformanceMonitor()
        
    def tearDown(self):
        self.monitor.stop()
        
    def test_initialization(self):
        self.assertTrue(hasattr(self.monitor, 'metrics'))
        self.assertTrue(isinstance(self.monitor.metrics, dict))
        self.assertIn('cpu_usage', self.monitor.metrics)
        self.assertIn('memory_usage', self.monitor.metrics)
        self.assertIn('network_activity', self.monitor.metrics)
        
    def test_metrics_recording(self):
        # Test CPU usage recording
        initial_cpu_len = len(self.monitor.metrics['cpu_usage'])
        self.monitor.record_cpu_usage()
        self.assertEqual(len(self.monitor.metrics['cpu_usage']), initial_cpu_len + 1)
        
        # Test memory usage recording
        initial_mem_len = len(self.monitor.metrics['memory_usage'])
        self.monitor.record_memory_usage()
        self.assertEqual(len(self.monitor.metrics['memory_usage']), initial_mem_len + 1)
        
        # Test network activity recording
        initial_net_len = len(self.monitor.metrics['network_activity'])
        self.monitor.record_network_activity()
        self.assertEqual(len(self.monitor.metrics['network_activity']), initial_net_len + 1)
        
    def test_thread_management(self):
        # Verify thread is running
        self.assertTrue(self.monitor.monitor_thread.is_alive())
        
        # Stop and verify thread termination
        self.monitor.stop()
        time.sleep(0.1)  # Allow time for thread to stop
        self.assertFalse(self.monitor.monitor_thread.is_alive())
        
    def test_metrics_content(self):
        # Verify metrics contain valid data
        self.monitor.record_cpu_usage()
        self.monitor.record_memory_usage()
        self.monitor.record_network_activity()
        
        self.assertIsInstance(self.monitor.metrics['cpu_usage'][-1], float)
        self.assertIsInstance(self.monitor.metrics['memory_usage'][-1], float)
        self.assertIsInstance(self.monitor.metrics['network_activity'][-1], dict)

if __name__ == "__main__":
    unittest.main()
