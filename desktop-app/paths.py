"""
Centralised path helpers for Screen Gaze.

Works identically whether running from source (``python main.py``) or from a
frozen PyInstaller ``.app`` bundle.
"""

import os
import sys

# ── bundle / project root ────────────────────────────────────────────────
def get_bundle_dir() -> str:
    """Return the root directory of the application.

    * **Frozen (PyInstaller)**  → ``sys._MEIPASS`` (the temporary extraction
      folder, or the ``Resources`` folder inside the ``.app``).
    * **Source**                → the directory that contains *this* file,
      which is the ``desktop-app/`` project root.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller sets sys._MEIPASS to the bundle's internal data dir
        return sys._MEIPASS          # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


# ── writable data directory ──────────────────────────────────────────────
def get_data_dir() -> str:
    """Return a writable directory for runtime data (databases, session
    files, etc.).

    * **Frozen** → ``~/Library/Application Support/ScreenGaze/``
    * **Source** → the project root (same as ``get_bundle_dir()``)

    The directory is created automatically if it does not exist.
    """
    if getattr(sys, "frozen", False):
        base = os.path.expanduser("~/Library/Application Support/ScreenGaze")
    else:
        base = get_bundle_dir()
    os.makedirs(base, exist_ok=True)
    return base


# ── resource resolver ────────────────────────────────────────────────────
def resource_path(relative: str) -> str:
    """Resolve *relative* against the bundle root.

    Use this for **read-only** bundled assets such as icons, ML models, the
    ``.env`` file, and ``schema.sql``.

    Parameters
    ----------
    relative : str
        A path relative to the project root, e.g.
        ``"assets/icons/login.svg"`` or ``"ml_dev_scripts/models/xgb_model_subject_3.json"``.
    """
    return os.path.join(get_bundle_dir(), relative)
