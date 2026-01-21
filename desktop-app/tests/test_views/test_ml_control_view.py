import pytest
from PySide6.QtCore import Qt
from view.ml_control_view import MLControlView
from viewmodel.ml_control_viewmodel import MLControlViewModel
from unittest.mock import MagicMock

"""
ML Control View Tests
---------------------
These tests use 'pytest-qt' to verify the UI Logic.
We check that:
1. Buttons are enabled/disabled correctly based on state.
2. Clicking buttons calls the correct ViewModel methods.
3. The UI updates when the ViewModel emits signals.
"""

@pytest.fixture
def viewmodel_mock(qtbot):
    """
    Mock the ViewModel completely. 
    Why: We want to test the VIEW (UI), not the business logic.
    Using a real ViewModel would require handling subprocesses etc.
    """
    vm = MagicMock(spec=MLControlViewModel)
    
    # We need to replicate the signals since they are accessed on init (connect)
    # MagicMock doesn't automatically behave like a Signal.
    # So we can just mock the connect method of the signals.
    vm.is_running_changed = MagicMock()
    vm.error_occurred = MagicMock()
    
    # Also properties
    vm.is_running = False 
    return vm

@pytest.fixture
def view(qtbot, viewmodel_mock):
    """
    Fixture that initializes the Widget and registers it with qtbot.
    qtbot tracks the widget to handle cleanup automatically.
    """
    widget = MLControlView(viewmodel_mock)
    qtbot.addWidget(widget)
    return widget

def test_initial_ui_state(view, viewmodel_mock):
    """Verify default UI: Label says Stopped, Start enabled, Stop disabled."""
    assert view.status_label.text() == "ML Algorithm: Stopped"
    assert view.start_button.isEnabled() is True
    assert view.stop_button.isEnabled() is False

def test_start_button_click(view, viewmodel_mock, qtbot):
    """Verify clicking 'Start' calls `viewmodel.start_ml_script()`."""
    qtbot.mouseClick(view.start_button, Qt.LeftButton)
    viewmodel_mock.start_ml_script.assert_called_once()

def test_stop_button_click(view, viewmodel_mock, qtbot):
    """Verify clicking 'Stop' calls `viewmodel.stop_ml_script()`."""
    # Enable stop button first to be clickable (simulating running state for this split second)
    view.stop_button.setEnabled(True)
    qtbot.mouseClick(view.stop_button, Qt.LeftButton)
    viewmodel_mock.stop_ml_script.assert_called_once()

def test_update_on_running_changed(view, viewmodel_mock):
    """
    Verify the UI updates correctly when `is_running` changes.
    We simulate this by calling the slot `on_running_changed` directly,
    mimicking a signal emission.
    """
    # Simulate signal emission: True (Running)
    view.on_running_changed(True)
    
    assert view.status_label.text() == "ML Algorithm: Running"
    assert view.start_button.isEnabled() is False
    assert view.stop_button.isEnabled() is True
    
    # Simulate signal emission: False (Stopped)
    view.on_running_changed(False)
    assert view.status_label.text() == "ML Algorithm: Stopped"
    assert view.start_button.isEnabled() is True
    assert view.stop_button.isEnabled() is False
