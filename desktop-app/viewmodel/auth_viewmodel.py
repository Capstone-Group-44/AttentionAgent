import webbrowser
import time
import threading
from PySide6.QtCore import QObject, Signal
from model.user import User
from flask import Flask, request
import os
from dotenv import load_dotenv


class AuthViewModel(QObject):
    load_dotenv()

    login_success = Signal(str)
    login_failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_user = None
        self._flask_app = Flask(__name__)
        self._server_thread = None

        @self._flask_app.route("/callback")  # Endpoint for OAuth callback
        def callback():
            # Extract user info from query params
            name = request.args.get("name")
            email = request.args.get("email")
            uid = request.args.get("uid")

            if name and email and uid:
                self.current_user = User(name=name, email=email, uid=uid)
                self.login_success.emit(name)
                return "Login successful! You can close this window."
            else:
                self.login_failed.emit("Missing user info")
                return "Login failed!", 400

    def start_local_server(self):
        self._server_thread = threading.Thread(
            target=lambda: self._flask_app.run(
                port=int(os.getenv("PORT")), debug=False, use_reloader=False)
        )
        self._server_thread.daemon = True
        self._server_thread.start()

    def login(self):
        self.start_local_server()
        # URL to the webapp login page
        webbrowser.open("http://localhost:3000/login")
        time.sleep(20)  # Wait for user to complete login in browser
        return True

    def register(self):
        webbrowser.open("http://localhost:3000/login")

    def get_current_username(self):
        if self.current_user:
            return self.current_user.username
        return None
