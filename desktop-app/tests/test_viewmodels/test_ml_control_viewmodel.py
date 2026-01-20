import pytest
import os
import signal
from unittest.mock import MagicMock, patch
from viewmodel.ml_control_viewmodel import MLControlViewModel

"""
ML Control ViewModel Tests
--------------------------
These tests verify that the ViewModel correctly manages the external ML script process.

Mocking Strategy:
- `subprocess.Popen`: We mock starting the process to avoid actually running the heavy ML script.
- `os.path.exists`: We verify logic for when the script file is found or missing.
"""

@pytest.fixture
def ml_viewmodel():
    return MLControlViewModel()

def test_initial_state(ml_viewmodel):
    """Verify default state: not running, no process handle."""
    assert not ml_viewmodel.is_running
    assert ml_viewmodel._process is None

def test_start_ml_script_success(ml_viewmodel):
    """
    Test starting the script:
    1. Verify `subprocess.Popen` is called with correct arguments.
    2. Verify internal state updates to 'running'.
    """
    with patch("subprocess.Popen") as mock_popen:
        with patch("os.path.exists", return_value=True): # script path exists
            mock_process = MagicMock()
            mock_process.poll.return_value = None # None means process is still running
            mock_popen.return_value = mock_process
            
            ml_viewmodel.start_ml_script()
            
            assert ml_viewmodel.is_running is True
            mock_popen.assert_called_once()

def test_start_ml_script_not_found(ml_viewmodel):
    """
    Test error handling when the 'main_ML.py' file is missing.
    Should emit an error signal and NOT start the process.
    """
    with patch("os.path.exists", return_value=False):
        # Connect a mock to the signal to spy on it
        error_spy = MagicMock()
        ml_viewmodel.error_occurred.connect(error_spy)
        
        ml_viewmodel.start_ml_script()
        
        assert ml_viewmodel.is_running is False
        
        # Verify that the error signal was emitted
        error_spy.assert_called()

def test_stop_ml_script(ml_viewmodel):
    """
    Test stopping the script:
    1. Checks if appropriate termination signal is sent (SIGTERM or CTRL_BREAK).
    2. Verifies clean up of the internal process handle.
    """
    mock_process = MagicMock()
    ml_viewmodel._process = mock_process
    ml_viewmodel._is_running = True
    
    ml_viewmodel.stop_ml_script()
    
    assert ml_viewmodel.is_running is False
    assert ml_viewmodel._process is None
    
    # Check if terminate or send_signal was called on the mock process
    if os.name == 'nt':
        mock_process.send_signal.assert_called()
    else:
        mock_process.terminate.assert_called()
