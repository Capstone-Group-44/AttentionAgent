import sys
import os
import pytest
from PySide6.QtWidgets import QApplication

# Add the project root (desktop-app) to sys.path so that we can import modules
# like 'model', 'viewmodel', 'view' from top-level packages.
# This assumes running pytest from 'desktop-app/' directory.
# If running specifically from 'tests/', we still need the parent dir.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture(scope="session")
def qapp():
    """
    Fixture to ensure a QApplication exists for the entire test session.
    pytest-qt provides its own 'qapp' fixture, but sometimes manual handling
    or ensuring singleton behavior is useful. 
    However, pytest-qt handles this well usually.
    We just return the instance if it exists.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
