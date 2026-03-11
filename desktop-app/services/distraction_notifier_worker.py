import time
from threading import Event

from db.focus_sample_repository import FocusSampleRepository
from services.notification_service import NotificationService


class DistractionNotifierWorker:
    """Background worker that periodically checks focus data and notifies the user when distracted."""

    DEFAULT_EVALUATION_WINDOW = 20   # seconds
    DEFAULT_COOLDOWN = 60            # seconds
    DISTRACTION_THRESHOLD = 0.50     # >50 % distracted triggers a notification

    def __init__(
        self,
        *,
        session_id: str,
        stop_event: Event,
        evaluation_window: int = DEFAULT_EVALUATION_WINDOW,
        cooldown: int = DEFAULT_COOLDOWN,
    ):
        self.session_id = session_id
        self.stop_event = stop_event
        self.evaluation_window = max(evaluation_window, 5)  # floor at 5 s
        self.cooldown = max(cooldown, 0)                    # floor at 0 s
        self._sample_repo = FocusSampleRepository()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _interruptible_sleep(self, seconds: int) -> bool:
        """Sleep in 1-second increments. Returns True if stop_event was set."""
        for _ in range(seconds):
            if self.stop_event.is_set():
                return True
            time.sleep(1)
        return self.stop_event.is_set()

    def _is_distracted(self) -> bool:
        """Query the local DB and return True when >50 % of recent samples are distracted."""
        states = self._sample_repo.get_recent_attention_states(
            self.session_id, seconds_ago=self.evaluation_window
        )
        if not states:
            return False  # no data yet – assume focused
        distracted_count = sum(1 for s in states if s == 0)
        return distracted_count / len(states) > self.DISTRACTION_THRESHOLD

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        """Entry point – intended to be called in a daemon thread."""
        while not self.stop_event.is_set():
            # 1. Wait for the evaluation window to fill up
            if self._interruptible_sleep(self.evaluation_window):
                break

            # 2. Evaluate focus
            if self._is_distracted():
                NotificationService.send_notification("gazeCam", "User is Distracted")
                # 3. Cooldown after sending a notification (skip if 0)
                if self.cooldown > 0:
                    if self._interruptible_sleep(self.cooldown):
                        break
            # If not distracted, loop immediately (waits another evaluation window)

