# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ScreenGaze (Windows).

Run with:
    pyinstaller ScreenGaze.win.spec
"""

import os
import sysconfig
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Project root (directory that contains this .spec file)
ROOT = SPECPATH

# Locate site-packages in the active environment (works for venv/conda)
_sp = sysconfig.get_paths().get("purelib") or ""

# Data files to bundle: (source_path, dest_folder_inside_dist)
datas = [
    (os.path.join(ROOT, ".env"), "."),
    (os.path.join(ROOT, "assets", "icons"), os.path.join("assets", "icons")),
    (os.path.join(ROOT, "db", "schema.sql"), "db"),
    (
        os.path.join(ROOT, "ml_dev_scripts", "models"),
        os.path.join("ml_dev_scripts", "models"),
    ),
    (
        os.path.join(ROOT, "ml_dev_scripts", "docs", "production_models"),
        os.path.join("ml_dev_scripts", "docs", "production_models"),
    ),
]

# Collect mediapipe data files (tflite models, binarypb configs)
datas += collect_data_files("mediapipe")

# Collect xgboost data files (VERSION file needed at import time)
datas += collect_data_files("xgboost")

# Optional: include Firebase key if present
firebase_key_dir = os.path.join(ROOT, "keys")
if os.path.isdir(firebase_key_dir):
    datas.append((firebase_key_dir, "keys"))

# Dynamic libs shipped by packages
binaries = []
binaries += collect_dynamic_libs("xgboost")
binaries += collect_dynamic_libs("mediapipe")

hiddenimports = [
    "mediapipe",
    "mediapipe.python",
    "mediapipe.python._framework_bindings",
    "cv2",
    "xgboost",
    "xgboost.core",
    "sklearn",
    "sklearn.utils._cython_blas",
    "sklearn.neighbors._typedefs",
    "sklearn.neighbors._quad_tree",
    "sklearn.tree._utils",
    "firebase_admin",
    "firebase_admin.credentials",
    "firebase_admin.firestore",
    "google.cloud.firestore",
    "google.cloud.firestore_v1",
    "google.api_core",
    "grpc",
    "flask",
    "PySide6",
    "PySide6.QtWidgets",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "dotenv",
    "numpy",
    "pandas",
    "joblib",
    "scipy",
    "paths",
    "model",
    "model.user",
    "view",
    "view.auth_view",
    "view.focus_view",
    "view.settings_view",
    "view.ml_control_view",
    "view.components",
    "viewmodel",
    "viewmodel.auth_viewmodel",
    "viewmodel.focus_viewmodel",
    "viewmodel.ml_control_viewmodel",
    "db",
    "db.database",
    "db.session_repository",
    "db.user_repository",
    "db.focus_sample_repository",
    "services",
    "services.focus_tracking_worker",
    "services.distraction_notifier_worker",
    "services.notification_service",
    "scripts",
    "scripts.build_reports",
    "ml_runner_scripts",
    "ml_runner_scripts.FocusPredictor",
]

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "pytest",
        "pytest_qt",
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Prefer an .ico if present; otherwise let PyInstaller use the default icon
_icon_ico = os.path.join(ROOT, "assets", "app_icon.ico")
_icon = _icon_ico if os.path.isfile(_icon_ico) else None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ScreenGaze",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="ScreenGaze",
)

