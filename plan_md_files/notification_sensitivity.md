# Configurable Distraction Notifier Settings

Add two input fields in **Settings → Notifications** to let the user adjust the distraction evaluation window and the notification cooldown. Propagate the values to the worker at session start.

## Proposed Changes

### Settings UI
#### [MODIFY] [settings_view.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/view/settings_view.py)
- Import `QLineEdit`.
- Inside the Notifications card (after the "Test Notification" button), add two labelled text fields:
  - **Distracted Time (seconds)** – `QLineEdit`, default `"20"`, minimum accepted value 5.
  - **Frequency of Notifications (seconds)** – `QLineEdit`, default `"60"`, minimum accepted value 0.
- Store them as `self.distracted_time_input` and `self.notif_freq_input`.
- Add two public accessor methods: `get_distracted_time_seconds() -> int` and `get_notif_frequency_seconds() -> int`.
  - Parse the text field value, enforce the minimum (5 / 0), and default to 20 / 60 on invalid input.

---

### Viewmodel
#### [MODIFY] [focus_viewmodel.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/viewmodel/focus_viewmodel.py)
- Accept an optional `settings_view` reference via a new `set_settings_view(view)` method.
- In `_start_ml_process()`, read `distracted_time` and `notif_frequency` from the settings view (falling back to defaults) and pass them to `DistractionNotifierWorker`.

---

### Worker
#### [MODIFY] [distraction_notifier_worker.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/services/distraction_notifier_worker.py)
- Accept `evaluation_window` and `cooldown` as constructor arguments (defaulting to 20 and 60).
- Use these instead of the class-level constants.
- When `cooldown == 0`, skip the cooldown sleep entirely and loop immediately back to the next evaluation window.

---

### Wiring
#### [MODIFY] [main.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/main.py)
- After creating `settings_view` and `focus_viewmodel`, call `self.focus_viewmodel.set_settings_view(self.settings_view)`.

## Verification Plan

### Manual Verification
1. Open Settings → Notifications. Confirm both fields appear with defaults (20, 60).
2. Set "Distracted Time" to 10 and "Frequency" to 0. Start a session. Look away 10 s → notification should fire immediately and re-fire every 10 s with no cooldown.
3. Set "Frequency" to 90 (1 min 30 s). After a distraction notification fires, verify the next one only comes after 90 s.
4. Enter invalid input (e.g. letters) → should fall back to defaults without crashing.
