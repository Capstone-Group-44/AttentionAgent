# Performance Improvements for Notification Delivery

The current implementation of the notification system in `desktop-app/services/notification_service.py` uses `subprocess.run(["osascript", ...])` on macOS and `subprocess.run(["powershell", ...])` on Windows.

`subprocess.run` is a **blocking** call, meaning the application’s worker thread pauses until the notification has fully displayed and the script finishes running.
- On macOS, `osascript` takes about ~0.25 seconds to execute.
- On Windows, `powershell` has a massive startup overhead and can take 1-2+ seconds to execute.

## Proposed Changes

We can improve the speed of the notification delivery with the following optimizations:

### 1. Make Notifications Non-Blocking (No new dependencies)
Change `subprocess.run` to `subprocess.Popen` in `notification_service.py`. 
- **Effect**: Fire-and-forget. The worker thread will immediately continue execution without waiting for the notification process to complete. This will fix any lag in the application's focus parsing loop.

### 2. Further Enhancements (Requires new dependencies)
If making it non-blocking doesn't feel fast enough (because the OS still takes time to render the notification), we can replace the underlying tools:
- **macOS**: Install `pync` (`pip install pync`), which uses a pre-compiled Objective-C binary that skips the `osascript` startup time, turning a 0.25s delay into <0.05s.
- **Windows**: Install `win10toast` (`pip install win10toast`), which uses native Windows APIs directly, dropping the 1-2 second PowerShell startup time to <0.05s.

## User Review Required
> [!IMPORTANT]  
> Please let me know:
> 1. Should I just implement **Step 1 (Non-Blocking)** first to see if that fixes the lag for you?
> 2. Or would you prefer I also implement **Step 2** and add the new dependencies (`pync` for Mac / `win10toast` for Windows) for the absolute fastest notification delivery?

### NotificationService Updates
#### [MODIFY] [notification_service.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/services/notification_service.py)
Change `subprocess.run` to `subprocess.Popen` in both OS methods to prevent blocking.

## Verification Plan
### Automated Tests
Currently, there are no specific integration tests for `NotificationService`. We will test it by running `pytest` to make sure existing tests pass.

### Manual Verification
1. Open the desktop app and start a session.
2. Trigger a distraction notification.
3. Observe if the notification appears quicker and doesn't halt the underlying tracking timer.
