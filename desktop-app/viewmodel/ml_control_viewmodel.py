import subprocess
import sys
import os
import signal
from PySide6.QtCore import QObject, Signal

class MLControlViewModel(QObject):
    is_running_changed = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._process = None
        self._is_running = False

    @property
    def is_running(self):
        return self._is_running

    def start_ml_script(self):
        if self._is_running and self._process and self._process.poll() is None:
            return

        try:
            # Construct path to main_ML.py
            # Assuming this is running from desktop-app/main.py, so app/main_ML.py is relative
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(base_dir, "app", "main_ML.py")
            working_dir = os.path.join(base_dir, "app")
            
            if not os.path.exists(script_path):
                self.error_occurred.emit(f"Script not found at: {script_path}")
                return

            # Use the same python interpreter as the current process
            creationflags = 0
            if os.name == "nt":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            self._process = subprocess.Popen(
                [sys.executable, "main_ML.py"],
                cwd=working_dir,
                creationflags=creationflags
            )
            self._is_running = True
            self.is_running_changed.emit(True)
        except Exception as e:
            self.error_occurred.emit(str(e))
            self._is_running = False
            self.is_running_changed.emit(False)

    def stop_ml_script(self): 
        if not self._process:
            return

        try:
            if os.name == "nt":
                self._process.send_signal(signal.CTRL_BREAK_EVENT) # For Windows
            else:
                self._process.send_signal(signal.SIGINT) # For Unix-like systems

            self._process.wait(timeout=5)
        except Exception:
            # If it doesn't terminate, kill it
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                    self._process.wait(timeout=5)   
                except Exception:
                    pass    
        self._process = None
        
        self._is_running = False
        self.is_running_changed.emit(False)
