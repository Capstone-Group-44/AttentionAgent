import sys
import os
import pytest
from PySide6.QtWidgets import QApplication

# -----------------------------------------------------------------------------
# Path Setup
# -----------------------------------------------------------------------------
# We need to add the project root (desktop-app) to sys.path so that tests can 
# import modules like 'model', 'viewmodel', 'view' from top-level packages.
#
# This setup assumes one of two common running scenarios:
# 1. Running 'pytest' from the 'desktop-app/' directory (PROJECT_ROOT is current dir).
# 2. Running 'pytest' from the 'tests/' directory (PROJECT_ROOT is parent dir).
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(scope="session")
def qapp():
    """
    Fixture to ensure a single QApplication instance exists for the entire test session.
    
    Why this is needed:
    - PySide6/Qt requires a QApplication to exist before creating any QWidgets.
    - Creating multiple QApplication instances causing crashing or errors.
    
    How it works:
    - We check QApplication.instance() to see if one already exists (e.g. created by pytest-qt).
    - If not, we create a new one.
    - Using scope="session" ensures this runs only once per test run.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
