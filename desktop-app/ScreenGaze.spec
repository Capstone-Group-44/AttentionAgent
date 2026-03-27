# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Screen Gaze – macOS .app bundle.

Run with:
    pyinstaller ScreenGaze.spec
"""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# ── project root (directory that contains this .spec file) ───────────
ROOT = SPECPATH

# ── Locate site-packages ─────────────────────────────────────────────
import site as _site
_sp = os.path.join(
    os.path.dirname(ROOT),  # AttentionAgent/
    '.venv311', 'lib', 'python3.11', 'site-packages'
)

# ── data files to bundle ─────────────────────────────────────────────
# (source_path, dest_folder_inside_bundle)
datas = [
    # .env config
    (os.path.join(ROOT, '.env'), '.'),
    # SVG icons
    (os.path.join(ROOT, 'assets', 'icons'), os.path.join('assets', 'icons')),
    # DB schema
    (os.path.join(ROOT, 'db', 'schema.sql'), 'db'),
    # XGBoost ML models
    (os.path.join(ROOT, 'ml_dev_scripts', 'models'), os.path.join('ml_dev_scripts', 'models')),
    # XGBoost production model (used by focus tracker)
    (os.path.join(ROOT, 'ml_dev_scripts', 'docs', 'production_models'), os.path.join('ml_dev_scripts', 'docs', 'production_models')),
]

# Collect mediapipe data files (tflite models, binarypb configs)
datas += collect_data_files('mediapipe')

# Collect xgboost data files (VERSION file needed at import time)
datas += collect_data_files('xgboost')

# Optional: include Firebase key if present
firebase_key_dir = os.path.join(ROOT, 'keys')
if os.path.isdir(firebase_key_dir):
    datas.append((firebase_key_dir, 'keys'))

# ── binary libraries ─────────────────────────────────────────────────
binaries = [
    # XGBoost native library — must be at xgboost/lib/libxgboost.dylib
    (
        os.path.join(_sp, 'xgboost', 'lib', 'libxgboost.dylib'),
        os.path.join('xgboost', 'lib'),
    ),
]
# Also collect any dynamic libs that xgboost and mediapipe ship
binaries += collect_dynamic_libs('xgboost')
binaries += collect_dynamic_libs('mediapipe')

# ── hidden imports ───────────────────────────────────────────────────
hiddenimports = [
    'mediapipe',
    'mediapipe.python',
    'mediapipe.python._framework_bindings',
    'cv2',
    'xgboost',
    'xgboost.core',
    'sklearn',
    'sklearn.utils._cython_blas',
    'sklearn.neighbors._typedefs',
    'sklearn.neighbors._quad_tree',
    'sklearn.tree._utils',
    'firebase_admin',
    'firebase_admin.credentials',
    'firebase_admin.firestore',
    'google.cloud.firestore',
    'google.cloud.firestore_v1',
    'google.api_core',
    'grpc',
    'flask',
    'PySide6',
    'PySide6.QtWidgets',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'dotenv',
    'numpy',
    'pandas',
    'joblib',
    'scipy',
    'paths',
    'model',
    'model.user',
    'view',
    'view.auth_view',
    'view.focus_view',
    'view.settings_view',
    'view.ml_control_view',
    'view.components',
    'viewmodel',
    'viewmodel.auth_viewmodel',
    'viewmodel.focus_viewmodel',
    'viewmodel.ml_control_viewmodel',
    'db',
    'db.database',
    'db.session_repository',
    'db.user_repository',
    'db.focus_sample_repository',
    'services',
    'services.focus_tracking_worker',
    'services.distraction_notifier_worker',
    'services.notification_service',
    'scripts',
    'scripts.build_reports',
    'ml_runner_scripts',
    'ml_runner_scripts.FocusPredictor',
]

# ── Analysis ─────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(ROOT, 'main.py')],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'pytest',
        'pytest_qt',
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ScreenGaze',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,                       # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, 'assets', 'app_icon.icns'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='ScreenGaze',
)

app = BUNDLE(
    coll,
    name='Screen Gaze.app',
    icon=os.path.join(ROOT, 'assets', 'app_icon.icns'),
    bundle_identifier='com.screengaze.app',
    info_plist={
        'CFBundleDisplayName': 'Screen Gaze',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSCameraUsageDescription': 'Screen Gaze needs camera access to track your gaze and measure focus.',
        'LSMinimumSystemVersion': '11.0',
    },
)
