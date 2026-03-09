import subprocess
import sys
import os
import signal
from PySide6.QtCore import QObject, Signal, QTimer

class FocusViewModel(QObject):
    # Signal emited with (time_string, progress_value_0_to_100)
    timer_update = Signal(str, float)
    session_started = Signal()
    session_stopped = Signal()
    break_started = Signal() # New signal when break starts
    focus_resumed = Signal() # New signal when break ends and focus resumes
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._process = None
        self._is_running = False
        
        # New State Management Variables
        self._mode = "idle" # "idle", "focus", "break"
        self._focus_total_seconds = 0
        self._focus_remaining_seconds = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_tick)
        
        self._total_seconds = 0
        self._remaining_seconds = 0

    @property
    def is_running(self):
        return self._is_running

    def _start_ml_process(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(base_dir, "app", "main_ML.py")
            working_dir = os.path.join(base_dir, "app")
            
            if not os.path.exists(script_path):
                self.error_occurred.emit(f"Script not found at: {script_path}")
                return False

            creationflags = 0
            if os.name == "nt":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            
            env = os.environ.copy()
            env["PYTHONPATH"] = working_dir + os.pathsep + env.get("PYTHONPATH", "")

            self._process = subprocess.Popen(
                [sys.executable, "main_ML.py"],
                cwd=working_dir,
                env=env,
                creationflags=creationflags,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                outs, errs = self._process.communicate(timeout=0.1)
                if self._process.returncode is not None and self._process.returncode != 0:
                     self.error_occurred.emit(f"ML Process failed: {errs}")
                     self._process = None
                     return False
            except subprocess.TimeoutExpired:
                pass
            
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False

    def _stop_ml_process(self):
        if self._process:
            try:
                if os.name == "nt":
                    self._process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    self._process.send_signal(signal.SIGINT)
                
                try:
                    self._process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._process.terminate()
                    self._process.wait(timeout=2)
            except Exception:
                try:
                    self._process.kill()
                except:
                    pass
            self._process = None

    def start_session(self, duration_minutes):
        if self._is_running and self._mode == "focus":
            return

        # Start the ML Process
        if not self._start_ml_process():
            self.stop_session()
            return
            
        # 2. Start the Timer
        self._total_seconds = int(duration_minutes) * 60
        self._remaining_seconds = self._total_seconds
        
        # Save focus state
        self._focus_total_seconds = self._total_seconds
        self._focus_remaining_seconds = self._remaining_seconds
        
        self._mode = "focus"
        self._is_running = True
        self.timer.start(1000) # 1 second interval
        
        # Emit initial state
        self._emit_timer_update()
        self.session_started.emit()

    def stop_session(self):
        # Stop Timer
        self.timer.stop()
        
        # Stop Process
        self._stop_ml_process()

        self._is_running = False
        self._mode = "idle"
        self.session_stopped.emit()

    def start_short_break(self, duration_minutes):
        if not self._is_running or self._mode == "break":
            return
            
        # 1. Pause focus timer data
        self._focus_remaining_seconds = self._remaining_seconds
        
        # 2. Stop ML process
        self._stop_ml_process()
        
        # 3. Start Break Timer
        self._mode = "break"
        self._total_seconds = int(duration_minutes) * 60
        self._remaining_seconds = self._total_seconds
        
        self._emit_timer_update()
        self.break_started.emit()

    def _on_timer_tick(self):
        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            self._emit_timer_update()
        else:
            if self._mode == "break":
                # Break finished. Resume Focus mode.
                self._mode = "focus"
                
                # Restore original focus state
                self._total_seconds = self._focus_total_seconds
                self._remaining_seconds = self._focus_remaining_seconds
                
                # Restart ML process
                if not self._start_ml_process():
                    self.stop_session()
                    return
                
                self._emit_timer_update()
                self.focus_resumed.emit()
            else:
                # Main focus session finished
                self.stop_session()

    def _emit_timer_update(self):
        mins = self._remaining_seconds // 60
        secs = self._remaining_seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"
        
        if self._total_seconds > 0:
            progress = ((self._total_seconds - self._remaining_seconds) / self._total_seconds) * 100
        else:
            progress = 0
            
        self.timer_update.emit(time_str, progress)
