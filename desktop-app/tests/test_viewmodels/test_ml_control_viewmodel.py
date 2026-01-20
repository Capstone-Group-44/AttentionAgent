import pytest
import os
import signal
from unittest.mock import MagicMock, patch
from viewmodel.ml_control_viewmodel import MLControlViewModel

@pytest.fixture
def ml_viewmodel():
    return MLControlViewModel()

def test_initial_state(ml_viewmodel):
    assert not ml_viewmodel.is_running
    assert ml_viewmodel._process is None

def test_start_ml_script_success(ml_viewmodel):
    with patch("subprocess.Popen") as mock_popen:
        with patch("os.path.exists", return_value=True): # script path exists
            mock_process = MagicMock()
            mock_process.poll.return_value = None # Process is running
            mock_popen.return_value = mock_process
            
            # Use spy to check signal
            # ml_viewmodel.is_running_changed.emit = MagicMock()
            
            ml_viewmodel.start_ml_script()
            
            assert ml_viewmodel.is_running is True
            mock_popen.assert_called_once()
            # ml_viewmodel.is_running_changed.emit.assert_called_with(True)

def test_start_ml_script_not_found(ml_viewmodel):
    with patch("os.path.exists", return_value=False):
        # Connect a mock to the signal to spy on it
        error_spy = MagicMock()
        ml_viewmodel.error_occurred.connect(error_spy)
        
        ml_viewmodel.start_ml_script()
        
        assert ml_viewmodel.is_running is False
        # Verify signal was emitted
        # The argument depends on the error string, we can just check called
        error_spy.assert_called()

def test_stop_ml_script(ml_viewmodel):
    mock_process = MagicMock()
    ml_viewmodel._process = mock_process
    ml_viewmodel._is_running = True
    
    ml_viewmodel.stop_ml_script()
    
    assert ml_viewmodel.is_running is False
    assert ml_viewmodel._process is None
    # Check if terminate or send_signal was called
    if os.name == 'nt':
        mock_process.send_signal.assert_called()
    else:
        mock_process.terminate.assert_called()
