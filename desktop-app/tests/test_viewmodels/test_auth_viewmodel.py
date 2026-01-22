import pytest
import threading
from unittest.mock import MagicMock, patch
from viewmodel.auth_viewmodel import AuthViewModel

"""
AuthViewModel Tests
-------------------
These tests cover the authentication logic, including login flow, callback handling,
and session management.

Mocking Strategy:
- `Flask`: We mock the Flask class preventing a real server from starting.
- `webbrowser`: We prevent the test from actually opening a browser window.
- `load_session`/`save_session`: We mock these methods to avoid reading/writing
  real session files on disk during tests.
"""

@pytest.fixture
def auth_viewmodel():
    """
    Standard fixture for AuthViewModel with all external dependencies mocked.
    use this for testing initialization, login flow initiation, and logout.
    """
    with patch("viewmodel.auth_viewmodel.Flask") as mock_flask:
        with patch("viewmodel.auth_viewmodel.load_dotenv"):
            # Mock loading session to avoid side effects from real .session.json
            with patch.object(AuthViewModel, 'load_session'):
                with patch.object(AuthViewModel, 'start_local_server'):
                     vm = AuthViewModel()
                     yield vm

def test_init(auth_viewmodel):
    """Verify that the ViewModel initializes correct defaults and attempts to load session."""
    assert auth_viewmodel.current_user is None
    assert auth_viewmodel._port == 5000
    auth_viewmodel.start_local_server.assert_called_once()
    auth_viewmodel.load_session.assert_called_once()

def test_login_starts_server_and_opens_browser(auth_viewmodel):
    """
    Test that calling login():
    1. Opens the system browser to the correct URL.
    2. Waits for the callback event.
    """
    with patch("viewmodel.auth_viewmodel.webbrowser.open") as mock_open:
        # Mock the server thread to assume it's running
        auth_viewmodel._server_thread = MagicMock()
        auth_viewmodel._server_thread.is_alive.return_value = True
        
        # Mock 'wait' to return True immediately, simulating a successful callback 
        # happening instantly.
        auth_viewmodel._callback_event.wait = MagicMock(return_value=True)
        
        result = auth_viewmodel.login(timeout=1.0)
        
        mock_open.assert_called_with(auth_viewmodel._web_login_url())
        assert result is True

def test_login_timeout(auth_viewmodel):
    """Test that login returns False if the callback event is never set within the timeout."""
    with patch("viewmodel.auth_viewmodel.webbrowser.open"):
        auth_viewmodel._server_thread = MagicMock()
        auth_viewmodel._server_thread.is_alive.return_value = True
        
        # Mock wait to return False (simulating a timeout)
        auth_viewmodel._callback_event.wait = MagicMock(return_value=False)
        
        result = auth_viewmodel.login(timeout=0.1)
        
        assert result is False
        assert auth_viewmodel._callback_error == "Timed out waiting for the login callback."

# -----------------------------------------------------------------------------
# Callback Route Tests
# -----------------------------------------------------------------------------
# For testing the callback, we actually want a mostly real Flask app (or at a minimum 
# the routing logic functioning) so we can use 'test_client' to simulate HTTP requests.

@pytest.fixture
def auth_viewmodel_with_real_flask():
    """
    Fixture that allows the Flask app to function normally (routing),
    but still prevents file I/O and server startup.
    """
    with patch("viewmodel.auth_viewmodel.load_dotenv"):
        with patch.object(AuthViewModel, 'load_session'):
            with patch.object(AuthViewModel, 'start_local_server'):
                vm = AuthViewModel()
                # Mock save_session to avoid writing to disk when user logs in
                vm.save_session = MagicMock()
                return vm

def test_callback_route_success(auth_viewmodel_with_real_flask):
    """
    Simulate a successful callback from the web app (Auth0/Next.js) 
    hitting our local Flask server.
    """
    vm = auth_viewmodel_with_real_flask
    client = vm._flask_app.test_client()
    
    # We spy on the 'login_success' signal to ensure it gets emitted
    success_signal_spy = MagicMock()
    vm.login_success.connect(success_signal_spy)
    
    # Simulate GET request with user data query parameters
    response = client.get("/callback?uid=123&username=test&email=test@a.com")
    
    assert response.status_code == 200
    assert vm.current_user is not None
    assert vm.current_user.uid == "123"
    
    # Verify the Vue/UI would receive the 'success' signal
    success_signal_spy.assert_called_with("test")

def test_callback_route_missing_info(auth_viewmodel_with_real_flask):
    """Test that the callback rejects requests missing required fields (like email)."""
    vm = auth_viewmodel_with_real_flask
    client = vm._flask_app.test_client()
    
    response = client.get("/callback?uid=123") # Missing email and username
    
    assert response.status_code == 400
    assert vm.current_user is None
    assert vm._callback_error == "Missing user information"

def test_logout(auth_viewmodel):
    """Test that logout clears the current user and tries to remove the session file."""
    auth_viewmodel.current_user = MagicMock()
    with patch("os.remove") as mock_remove:
        # Pretend the file exists so we can test removal
        with patch("os.path.exists", return_value=True):
            auth_viewmodel.logout()
            
            assert auth_viewmodel.current_user is None
            mock_remove.assert_called()
