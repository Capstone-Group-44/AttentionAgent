<<<<<<< HEAD
import threading
import time
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QGuiApplication

from db.session_repository import SessionRepository
from db.user_repository import UserRepository
from services.focus_tracking_worker import FocusTrackingWorker
=======
import subprocess
import sys
import os
import signal
from PySide6.QtCore import QObject, Signal, QTimer
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728

class FocusViewModel(QObject):
    # Signal emited with (time_string, progress_value_0_to_100)
    timer_update = Signal(str, float)
    session_started = Signal()
    session_stopped = Signal()
<<<<<<< HEAD
    error_occurred = Signal(str)

    def __init__(self, auth_viewmodel=None):
        super().__init__()
        self._auth_viewmodel = auth_viewmodel
        self._is_running = False
        self._stop_event = None
        self._worker_thread = None
        self._session_id = None
        self._session_start_ts = None

        self._user_repo = UserRepository()
        self._session_repo = SessionRepository()
=======
    break_started = Signal(str) # New signal when break starts, passing the name of the break
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
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_tick)
        
        self._total_seconds = 0
        self._remaining_seconds = 0

    @property
    def is_running(self):
        return self._is_running

<<<<<<< HEAD
    def start_session(self, duration_minutes):
        if self._is_running:
            return

        try:
            user = self._auth_viewmodel.current_user

            minutes = int(duration_minutes)
            if minutes <= 0:
                self.error_occurred.emit("Duration must be greater than 0.")
                return

            self._user_repo.create_user_with_id(
                user_id=user.uid,
                username=user.username,
                display_name=user.display_name or user.username,
                email=user.email,
                created_at=user.created_at,
            )

            width, height = self._get_screen_size()
            self._session_id = self._session_repo.start_session(
                user_id=user.uid,
                screen_width=width,
                screen_height=height,
            )
            self._session_start_ts = time.time()

            self._stop_event = threading.Event()
            worker = FocusTrackingWorker(
                user_id=user.uid,
                session_id=self._session_id,
                stop_event=self._stop_event,
                error_callback=self.error_occurred.emit,
            )
            self._worker_thread = threading.Thread(target=worker.run, daemon=True)
            self._worker_thread.start()

            self._total_seconds = minutes * 60
            self._remaining_seconds = self._total_seconds
            self.timer.start(1000)
            
            self._is_running = True
            self._emit_timer_update()
            self.session_started.emit()
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.stop_session()

    def stop_session(self):
        self.timer.stop()

        if self._stop_event is not None:
            self._stop_event.set()

        if self._worker_thread and self._worker_thread.is_alive():
            try:
                self._worker_thread.join(timeout=3)
            except Exception:
                pass

        duration_seconds = 0.0
        if self._session_start_ts is not None:
            duration_seconds = max(0.0, time.time() - self._session_start_ts)

        if self._session_id is not None:
            try:
                self._session_repo.end_session(self._session_id, duration_seconds)
            except Exception as exc:
                self.error_occurred.emit(f"Failed to end session in DB: {exc}")

        self._is_running = False
        self._session_id = None
        self._session_start_ts = None
        self._stop_event = None
        self._worker_thread = None
        self.session_stopped.emit()

=======
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

    def start_break(self, duration_minutes, break_name="Short Break"):
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
        self.break_started.emit(break_name)

>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
    def _on_timer_tick(self):
        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            self._emit_timer_update()
        else:
<<<<<<< HEAD
            self.stop_session()
=======
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
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728

    def _emit_timer_update(self):
        mins = self._remaining_seconds // 60
        secs = self._remaining_seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"
        
        if self._total_seconds > 0:
            progress = ((self._total_seconds - self._remaining_seconds) / self._total_seconds) * 100
        else:
            progress = 0
            
        self.timer_update.emit(time_str, progress)
<<<<<<< HEAD

    def _get_screen_size(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return 0, 0
        size = screen.size()
        return int(size.width()), int(size.height())
=======
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
