import webbrowser
import time
import threading
from model.user import User
from flask import Flask, request
from firebase_admin import auth, credentials, initialize_app


class AuthViewModel:
    def __init__(self):
        self.current_user = None

        cred = credentials.Certificate("path/to/serviceAccountKey.json")
        initialize_app(cred)

        self._flask_app = Flask(__name__)
        self._server_thread = None

        @self._flask_app.route("/callback")  # Endpoint for OAuth callback
        def callback():
            id_token = request.args.get("idToken")  # Secure JWT from webapp
            try:
                decoded_token = auth.verify_id_token(id_token)
                userId = decoded_token["userId"]
                name = decoded_token.get("name", "Unknown")
                email = decoded_token.get("email", "")

                self.current_user = User(userId=userId, name=name, email=email)

                # Emit signal to update UI
                self.login_success.emit(name)

                return "Login successful! You can close this window."
            except Exception as e:
                return f"Login failed: {e}", 400

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
