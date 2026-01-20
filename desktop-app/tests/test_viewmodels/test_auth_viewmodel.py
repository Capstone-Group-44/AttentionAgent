import pytest
import threading
from unittest.mock import MagicMock, patch
from viewmodel.auth_viewmodel import AuthViewModel

@pytest.fixture
def auth_viewmodel():
    with patch("viewmodel.auth_viewmodel.Flask") as mock_flask:
        with patch("viewmodel.auth_viewmodel.load_dotenv"):
            # Mock loading session to avoid side effects from real .session.json
            with patch.object(AuthViewModel, 'load_session'):
                with patch.object(AuthViewModel, 'start_local_server'):
                     vm = AuthViewModel()
                     yield vm

def test_init(auth_viewmodel):
    assert auth_viewmodel.current_user is None
    assert auth_viewmodel._port == 5000
    auth_viewmodel.start_local_server.assert_called_once()
    auth_viewmodel.load_session.assert_called_once()

def test_login_starts_server_and_opens_browser(auth_viewmodel):
    with patch("viewmodel.auth_viewmodel.webbrowser.open") as mock_open:
        # Mock the server thread to assume it's running
        auth_viewmodel._server_thread = MagicMock()
        auth_viewmodel._server_thread.is_alive.return_value = True
        
        # Mock wait behavior
        auth_viewmodel._callback_event.wait = MagicMock(return_value=True)
        
        result = auth_viewmodel.login(timeout=1.0)
        
        mock_open.assert_called_with("http://localhost:3000/login")
        assert result is True

def test_login_timeout(auth_viewmodel):
    with patch("viewmodel.auth_viewmodel.webbrowser.open"):
        auth_viewmodel._server_thread = MagicMock()
        auth_viewmodel._server_thread.is_alive.return_value = True
        
        # Mock wait to return False (timeout)
        auth_viewmodel._callback_event.wait = MagicMock(return_value=False)
        
        result = auth_viewmodel.login(timeout=0.1)
        
        assert result is False
        assert auth_viewmodel._callback_error == "Timed out waiting for the login callback."

# Redefining fixture to use real Flask for callback testing
@pytest.fixture
def auth_viewmodel_with_real_flask():
    with patch("viewmodel.auth_viewmodel.load_dotenv"):
        with patch.object(AuthViewModel, 'load_session'):
            with patch.object(AuthViewModel, 'start_local_server'):
                vm = AuthViewModel()
                # Mock save_session to avoid file I/O
                vm.save_session = MagicMock()
                return vm

def test_callback_route_success(auth_viewmodel_with_real_flask):
    vm = auth_viewmodel_with_real_flask
    client = vm._flask_app.test_client()
    
    # Setup signal spy
    success_signal_spy = MagicMock()
    vm.login_success.connect(success_signal_spy)
    
    response = client.get("/callback?uid=123&username=test&email=test@a.com")
    
    assert response.status_code == 200
    assert vm.current_user is not None
    assert vm.current_user.uid == "123"
    
    # Check if signal was emitted
    success_signal_spy.assert_called_with("test")

def test_callback_route_missing_info(auth_viewmodel_with_real_flask):
    vm = auth_viewmodel_with_real_flask
    client = vm._flask_app.test_client()
    
    response = client.get("/callback?uid=123") # Missing email and username
    
    assert response.status_code == 400
    assert vm.current_user is None
    assert vm._callback_error == "Missing user information"

def test_logout(auth_viewmodel):
    auth_viewmodel.current_user = MagicMock()
    with patch("os.remove") as mock_remove:
        with patch("os.path.exists", return_value=True):
            auth_viewmodel.logout()
            
            assert auth_viewmodel.current_user is None
            mock_remove.assert_called()
