import tkinter as tk
from tkinter import messagebox
import logging
import datetime
import os
import sys

class DebugApp:
    def __init__(self, root):
        self.root = root
        self.setup_logging()
        self.setup_ui()
        self.test_components()

    def setup_logging(self):
        """Configure logging to file and console"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Debug application started")

    def setup_ui(self):
        """Set up the debug interface"""
        self.root.title("Nova AI Debug Console")
        self.root.geometry("800x600")
        
        # Text area for logs
        self.text_area = tk.Text(self.root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Button frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        # Test buttons
        tests = [
            ("Test AppController", self.test_appcontroller),
            ("Test Interface", self.test_interface),
            ("Check Imports", self.check_imports)
        ]
        
        for text, command in tests:
            btn = tk.Button(btn_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

    def log(self, message, level=logging.INFO):
        """Log message and display in UI"""
        self.logger.log(level, message)
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.see(tk.END)

    def test_components(self):
        """Initial component tests"""
        self.log("Running initial component tests...")
        self.check_imports()
        
    def check_imports(self):
        """Check if required modules can be imported"""
        self.log("\nChecking imports...")
        modules = [
            'app_controller',
            'interface',
            'antivirus_agent_ai',
            'tkinter'
        ]
        
        for module in modules:
            try:
                __import__(module)
                self.log(f"SUCCESS: {module} imported")
            except Exception as e:
                self.log(f"ERROR importing {module}: {str(e)}", logging.ERROR)

    def test_appcontroller(self):
        """Test AppController functionality"""
        self.log("\nTesting AppController...")
        try:
            from app_controller import AppController
            controller = AppController()
            self.log("AppController initialized successfully")
            
            # Test antivirus scan
            result = controller.run_antivirus()
            self.log(f"Antivirus scan result: {result}")
            
        except Exception as e:
            self.log(f"AppController test failed: {str(e)}", logging.ERROR)

    def test_interface(self):
        """Test Interface module"""
        self.log("\nTesting Interface module...")
        try:
            from interface import speak_to_user
            speak_to_user("Test message from debug console")
            self.log("TTS test completed - you should hear the message")
        except Exception as e:
            self.log(f"Interface test failed: {str(e)}", logging.ERROR)

if __name__ == "__main__":
    root = tk.Tk()
    app = DebugApp(root)
    root.mainloop()
