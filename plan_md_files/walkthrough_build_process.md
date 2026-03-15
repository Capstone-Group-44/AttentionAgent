# Screen Gaze — macOS App Packaging Walkthrough

## Summary

Packaged the Screen Gaze desktop app as a native **macOS `.app` bundle** with a **DMG installer**, so anyone can download, double-click to install, and run it without Python.

## New Files

| File | Purpose |
|------|---------|
| [paths.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/paths.py) | Central path helper — resolves resources correctly in both source and frozen PyInstaller contexts |
| [ScreenGaze.spec](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/ScreenGaze.spec) | PyInstaller config — bundles data files, hidden imports, app icon, camera permission |
| [build_macos.sh](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/build_macos.sh) | One-command build script (`bash build_macos.sh --dmg`) |
| [app_icon.icns](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/assets/app_icon.icns) | macOS app icon |

## Modified Files

All `__file__`-based path references updated to use `paths.py`:

| File | Change |
|------|--------|
| [database.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/db/database.py) | SQLite DB → `~/Library/Application Support/ScreenGaze/`; schema loaded via `resource_path()` |
| [auth_viewmodel.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/viewmodel/auth_viewmodel.py) | Session file → writable data dir; `.env` loaded from bundle |
| [auth_view.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/view/auth_view.py) | Icons path → `resource_path()` |
| [focus_tracking_worker.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/services/focus_tracking_worker.py) | ML model + Firebase key → `resource_path()` |
| [focus_viewmodel.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/viewmodel/focus_viewmodel.py) | Firebase key paths → `resource_path()` |
| [ml_control_viewmodel.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/viewmodel/ml_control_viewmodel.py) | Script path → `resource_path()` |
| [main.py](file:///Users/sgsst/Documents/SYSC%204907/AttentionAgent/desktop-app/main.py) | Added early `.env` loading + `multiprocessing.freeze_support()` |

## Build Output

| Artifact | Size |
|----------|------|
| `dist/Screen Gaze.app` | 674 MB |
| `dist/ScreenGaze.dmg` | 240 MB |

The `.app` bundles: SVG icons, XGBoost models (4 JSON files + joblib pipeline), `schema.sql`, `.env`, and all Python dependencies (PySide6, mediapipe, opencv, xgboost, etc.).

## How to Build

```bash
cd desktop-app

# Build .app only
bash build_macos.sh

# Build .app + DMG installer
bash build_macos.sh --dmg
```

## How to Install (End User)

1. Open `ScreenGaze.dmg`
2. Drag **Screen Gaze** → **Applications**
3. Launch from Applications or Spotlight
4. macOS will prompt for camera permission on first focus session

## Architecture Note

When running as a packaged `.app`:
- **Read-only** resources (icons, models, schema) are inside the app bundle via `resource_path()`
- **Writable** data (SQLite DB, session file) goes to `~/Library/Application Support/ScreenGaze/` via `get_data_dir()`
- When running from source (`python main.py`), all paths resolve to the project root as before — **no behavior change**
