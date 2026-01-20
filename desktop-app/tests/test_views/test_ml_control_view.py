import pytest
from PySide6.QtCore import Qt
from view.ml_control_view import MLControlView
from viewmodel.ml_control_viewmodel import MLControlViewModel
from unittest.mock import MagicMock

@pytest.fixture
def viewmodel_mock(qtbot):
    # We can use a real instance or a mock. 
    # Using a real instance might trigger real subprocess/file ops which we want to avoid or mock.
    # It's better to mock the viewmodel for view testing.
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
    widget = MLControlView(viewmodel_mock)
    qtbot.addWidget(widget)
    return widget

def test_initial_ui_state(view, viewmodel_mock):
    assert view.status_label.text() == "ML Algorithm: Stopped"
    assert view.start_button.isEnabled() is True
    assert view.stop_button.isEnabled() is False

def test_start_button_click(view, viewmodel_mock, qtbot):
    qtbot.mouseClick(view.start_button, Qt.LeftButton)
    viewmodel_mock.start_ml_script.assert_called_once()

def test_stop_button_click(view, viewmodel_mock, qtbot):
    # Enable stop button first to be clickable
    view.stop_button.setEnabled(True)
    qtbot.mouseClick(view.stop_button, Qt.LeftButton)
    viewmodel_mock.stop_ml_script.assert_called_once()

def test_update_on_running_changed(view, viewmodel_mock):
    # Simulate signal emission logic calling the slot directly
    view.on_running_changed(True)
    
    assert view.status_label.text() == "ML Algorithm: Running"
    assert view.start_button.isEnabled() is False
    assert view.stop_button.isEnabled() is True
    
    view.on_running_changed(False)
    assert view.status_label.text() == "ML Algorithm: Stopped"
    assert view.start_button.isEnabled() is True
    assert view.stop_button.isEnabled() is False
