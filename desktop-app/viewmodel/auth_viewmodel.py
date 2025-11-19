import webbrowser
import time
import threading
from model.user import User
from flask import Flask, request


class AuthViewModel:
    def __init__(self):
        self.current_user = None
        self._flask_app = Flask(__name__)
        self._server_thread = None

        @self._flask_app.route("/callback")  # Endpoint for OAuth callback
        def callback():
            # Extract user info from query params
            name = request.args.get("name")
            email = request.args.get("email")
            uid = request.args.get("uid")

            self.current_user = User(uid=uid, name=name, email=email)

            return "Login successful! You can close this window."

    def start_local_server(self):
        self._server_thread = threading.Thread(
            target=lambda: self._flask_app.run(
                port=5000, debug=False, use_reloader=False)
        )
        self._server_thread.daemon = True
        self._server_thread.start()

    def login(self):
        self.start_local_server()
        webbrowser.open("#")  # URL to the webapp login page
        time.sleep(2)  # Wait for user to complete login in browser
        return True

    def register(self):
        webbrowser.open("#")

    def get_current_display_name(self):
        if self.current_user:
            return self.current_user.display_name
        return None
