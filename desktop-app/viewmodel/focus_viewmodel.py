import threading
import time
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QGuiApplication

from db.session_repository import SessionRepository
from db.user_repository import UserRepository
from services.focus_tracking_worker import FocusTrackingWorker


class FocusViewModel(QObject):
    # Signal emited with (time_string, progress_value_0_to_100)
    timer_update = Signal(str, float)
    session_started = Signal()
    session_stopped = Signal()
    # New signal when break starts, passing the name of the break
    break_started = Signal(str)
    focus_resumed = Signal()  # New signal when break ends and focus resumes
    error_occurred = Signal(str)
    # Signal emitted with numpy.ndarray containing the frame
    frame_ready = Signal(object)

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

        # New State Management Variables
        self._mode = "idle"  # "idle", "focus", "break"
        self._focus_total_seconds = 0
        self._focus_remaining_seconds = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_tick)

        self._total_seconds = 0
        self._remaining_seconds = 0

    @property
    def is_running(self):
        return self._is_running

    def _start_ml_process(self) -> bool:
        try:
            if self._auth_viewmodel is None or getattr(self._auth_viewmodel, "current_user", None) is None:
                self.error_occurred.emit(
                    "You must be logged in to start a session.")
                return False

            user = self._auth_viewmodel.current_user

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
                frame_callback=self._on_frame_received,
            )
            self._worker_thread = threading.Thread(
                target=worker.run, daemon=True)
            self._worker_thread.start()
            return True
        except Exception as e:
            try:
                self._stop_ml_process()
            except Exception:
                pass
            self.error_occurred.emit(str(e))
            return False

    def _stop_ml_process(self):
        stop_event = self._stop_event
        if stop_event is not None:
            try:
                stop_event.set()
            except Exception:
                pass

        worker_thread = self._worker_thread
        if worker_thread is not None and worker_thread.is_alive():
            try:
                worker_thread.join(timeout=3)
            except Exception:
                pass

        duration_seconds = 0.0
        if self._session_start_ts is not None:
            duration_seconds = max(0.0, time.time() - self._session_start_ts)

        if self._session_id is not None:
            try:
                self._session_repo.end_session(
                    self._session_id, duration_seconds)
            except Exception as exc:
                self.error_occurred.emit(f"Failed to end session in DB: {exc}")

        self._stop_event = None
        self._worker_thread = None
        self._session_id = None
        self._session_start_ts = None

    def start_session(self, duration_minutes):
        try:
            minutes = int(duration_minutes)
        except (TypeError, ValueError):
            self.error_occurred.emit("Duration must be a number of minutes.")
            return

        if minutes <= 0:
            self.error_occurred.emit("Duration must be greater than 0.")
            return

        if self._is_running:
            self.stop_session()

        # Start the ML Process
        if not self._start_ml_process():
            return

        # 2. Start the Timer
        self._total_seconds = minutes * 60
        self._remaining_seconds = self._total_seconds

        # Save focus state
        self._focus_total_seconds = self._total_seconds
        self._focus_remaining_seconds = self._remaining_seconds

        self._mode = "focus"
        self._is_running = True
        self.timer.start(1000)  # 1 second interval

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
            progress = (
                (self._total_seconds - self._remaining_seconds) / self._total_seconds) * 100
        else:
            progress = 0

        self.timer_update.emit(time_str, progress)

    def _get_screen_size(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return 0, 0
        size = screen.size()
        return int(size.width()), int(size.height())

    def _on_frame_received(self, frame):
        self.frame_ready.emit(frame)
