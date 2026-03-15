# Package Screen Gaze as a macOS Application

The Screen Gaze desktop app is currently a Python script (`main.py`) run from the terminal. The goal is to package it as a native macOS `.app` bundle with a DMG installer so anyone can download, install, and run it without needing Python or `pip install`.

## User Review Required

> [!IMPORTANT]
> **Firebase Credentials**: The app references a Firebase admin SDK key at `keys/attention-agent-30bd0-firebase-adminsdk-...json`. This directory doesn't currently exist in the project. The packaged app will skip Firebase (Firestore sync) gracefully when the key is absent, which is the existing behavior. If you need Firebase in the distributed app, you'll need to provide the key file and we'll bundle it.

> [!WARNING]
> **Writable data**: The packaged `.app` bundle is read-only. Files that the app writes at runtime (SQLite database, `.session.json`) need to be stored in the user's `~/Library/Application Support/ScreenGaze/` directory instead of alongside the source files. This is a small but important change.

> [!CAUTION]
> **App size**: Bundling mediapipe, opencv, numpy, xgboost, pandas, scikit-learn, and PySide6 will produce a large `.app` (likely 500MB–1GB+). This is expected for an ML-heavy Python app.

## Proposed Changes

### Path Helper Module

#### [NEW] [paths.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/paths.py)

A central utility module that resolves file paths correctly whether running from source or from a frozen PyInstaller bundle:

- `get_bundle_dir()` → returns the app's root directory (source checkout or `.app` Resources folder)
- `get_data_dir()` → returns a writable `~/Library/Application Support/ScreenGaze/` directory for runtime data (databases, session files)
- `resource_path(relative)` → resolves a bundled read-only resource path (assets, models, schema)

---

### Source File Path Updates

#### [MODIFY] [database.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/db/database.py)

- Change `db_path` to use `get_data_dir()` so the SQLite database is written to `~/Library/Application Support/ScreenGaze/`
- Change `schema.sql` loading to use `resource_path()`
- Copy `schema.sql` on first run if needed

#### [MODIFY] [auth_viewmodel.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/viewmodel/auth_viewmodel.py)

- Change `.session.json` path to use `get_data_dir()`
- Change `.env` loading to use `resource_path()` for the bundled `.env`

#### [MODIFY] [auth_view.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/view/auth_view.py)

- Change icons path to use `resource_path("assets/icons")`

#### [MODIFY] [focus_tracking_worker.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/services/focus_tracking_worker.py)

- Change ML model path to use `resource_path()`
- Change Firebase key path to use `resource_path()`

#### [MODIFY] [focus_viewmodel.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/viewmodel/focus_viewmodel.py)

- Change Firebase key path references to use `resource_path()`

#### [MODIFY] [main.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/main.py)

- Add early `dotenv` loading using `resource_path(".env")`

---

### Build Configuration

#### [NEW] [ScreenGaze.spec](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/ScreenGaze.spec)

PyInstaller spec file that:
- Sets the entry point to `main.py`
- Bundles data files: `.env`, `assets/icons/*.svg`, `db/schema.sql`, `ml_dev_scripts/models/*.json`
- Adds hidden imports for `mediapipe`, `firebase_admin`, `xgboost`, etc.
- Configures macOS `.app` bundle with name "Screen Gaze", bundle ID, and icon
- Sets `osx_bundle_identifier` to `com.screengaze.app`

#### [NEW] [build_macos.sh](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/build_macos.sh)

Shell script that:
1. Creates/activates the venv
2. Installs PyInstaller
3. Runs `pyinstaller ScreenGaze.spec`
4. Optionally creates a DMG using `hdiutil`

#### [NEW] [app_icon.icns](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/assets/app_icon.icns)

macOS app icon generated from a design and converted to `.icns` format.

---

## Verification Plan

### Manual Verification (User)

1. **Build the app**: Run `bash build_macos.sh` from the `desktop-app/` directory
2. **Check the output**: Verify `dist/Screen Gaze.app` exists  
3. **Launch the app**: Double-click `dist/Screen Gaze.app` — it should open the login screen
4. **Test login flow**: Click Login → browser should open → complete login → app should show focus view
5. **Test focus session**: Start a focus session → camera feed should appear → ML predictions should work
6. **Check data persistence**: Verify `~/Library/Application Support/ScreenGaze/` contains the SQLite database and session file
7. **Test DMG**: Open the generated `dist/ScreenGaze.dmg` and drag the app to Applications
8. **Test from Applications**: Launch from `/Applications/Screen Gaze.app` and verify everything works

### Automated Tests

- Existing tests in `tests/` should continue to pass when run from source:
  ```bash
  cd desktop-app && python -m pytest tests/ -v
  ```
