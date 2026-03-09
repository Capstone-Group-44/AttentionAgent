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
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_tick)
        
        self._total_seconds = 0
        self._remaining_seconds = 0

    @property
    def is_running(self):
        return self._is_running

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

    def _on_timer_tick(self):
        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            self._emit_timer_update()
        else:
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

    def _get_screen_size(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return 0, 0
        size = screen.size()
        return int(size.width()), int(size.height())
