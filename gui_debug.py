import tkinter as tk
from tkinter import messagebox
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Debug Console")
        self.setup_ui()
        self.test_components()

    def setup_ui(self):
        self.text = tk.Text(self.root, height=20, width=60)
        self.text.pack(padx=10, pady=10)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="Test AppController", 
                command=self.test_controller).pack(side=tk.LEFT, padx=5)
                
        tk.Button(btn_frame, text="Test Interface", 
                command=self.test_interface).pack(side=tk.LEFT, padx=5)

    def log(self, message):
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)
        logger.info(message)

    def test_components(self):
        self.log("Testing components...")
        
        # Test AppController
        try:
            from app_controller import AppController
            self.log("AppController import SUCCESS")
            self.controller = AppController()
            self.log("AppController initialization SUCCESS")
        except Exception as e:
            self.log(f"AppController ERROR: {str(e)}")
            messagebox.showerror("Error", f"AppController error: {str(e)}")

        # Test Interface
        try:
            from interface import speak_to_user
            self.log("Interface import SUCCESS")
            speak_to_user("Test message")
            self.log("Interface TTS SUCCESS") 
        except Exception as e:
            self.log(f"Interface ERROR: {str(e)}")
            messagebox.showerror("Error", f"Interface error: {str(e)}")

    def test_controller(self):
        self.log("\nTesting AppController...")
        try:
            result = self.controller.run_antivirus()
            self.log(f"Antivirus test: {result}")
        except Exception as e:
            self.log(f"Controller test failed: {str(e)}")

    def test_interface(self):
        self.log("\nTesting Interface...")
        try:
            from interface import speak_to_user
            speak_to_user("Interface test message")
            self.log("Voice output should have worked")
        except Exception as e:
            self.log(f"Interface test failed: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DebugApp(root)
    root.mainloop()
