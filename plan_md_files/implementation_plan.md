# Fix Camera Feed Freezing Implementation Plan

## Problem Description
Currently, when the user moves out of the camera frame, the `FocusTrackingWorker` continues to capture frames but skips processing them because MediaPipe `face_mesh.process()` does not return any `multi_face_landmarks`. In the existing code, a `continue` statement skips the rest of the loop, which means the `frame_callback` to the UI is never triggered. As a result, the camera feed in the desktop app freezes on the last visible frame until the user re-enters the frame.

## Proposed Changes

### `services/focus_tracking_worker.py`
We will re-structure the loop in `FocusTrackingWorker.run()` to separate the ML extraction/database logic from the UI display logic. 

Specifically:
- Initialize default text/status values indicating "NO FACE" or score of `0.0`.
- Place the existing extraction/database insertion code inside an `if results.multi_face_landmarks:` block. 
- Ensure that the UI drawing block (`cv2.putText` and `cv2.imshow`) and `self.frame_callback(frame)` executes in every iteration of the loop, whether a face is found or not.

This ensures that frames are continually sent to the `FocusView` on the main thread, unfreezing the camera when the user moves out of frame.

## Verification Plan
### Manual Verification
1. Launch the application (since it's a desktop app, I will ask you to run it via `python main.py` or equivalent).
2. Start a Focus Session with the camera.
3. Validate that the camera stream works correctly while the face is in view.
4. Move entirely out of the camera's view.
5. Verify that the camera stream shows the background live and continues to update, with the text overlay indicating "NO FACE" in red on the top left.
6. Verify normal functionality resumes as expected when moving back into the frame.
