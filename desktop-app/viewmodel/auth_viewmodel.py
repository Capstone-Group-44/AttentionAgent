import os
import threading
import json
from datetime import datetime
from typing import Optional

import webbrowser
from dotenv import load_dotenv
from flask import Flask, request
from PySide6.QtCore import QObject, Signal

from model.user import User


load_dotenv()

def _join_url(base: str, path: str) -> str:
    base = (base or "").rstrip("/")
    path = (path or "").strip()
    if not path.startswith("/"):
        path = "/" + path
    return base + path

class AuthViewModel(QObject):
    login_success = Signal(str)
    login_failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_user: Optional[User] = None
        self._port = int(os.getenv("PORT", "5000"))
        self._flask_app = Flask(__name__)
        self._server_thread: Optional[threading.Thread] = None
        self._callback_event = threading.Event()
        self._callback_error: Optional[str] = None
        self._session_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".session.json")

        # Web app URLs (env-driven)
        self._web_app_base_url = os.getenv("WEB_APP_BASE_URL", "http://localhost:3000")
        self._web_login_path = os.getenv("WEB_APP_LOGIN_PATH", "/login")
        self._web_register_path = os.getenv("WEB_APP_REGISTER_PATH", "/register")

        self._setup_routes()
        self.load_session()
        self.start_local_server()


    def _setup_routes(self):
        @self._flask_app.after_request
        def _add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            return response

        @self._flask_app.route("/callback", methods=["OPTIONS", "GET", "POST"])
        def callback():
            if request.method == "OPTIONS":
                return "", 204

            payload = request.get_json(silent=True) or {}
            payload.update(request.args.to_dict())

            name = (
                payload.get("name")
                or payload.get("display_name")
                or payload.get("displayName")
                or payload.get("username")
            )
            email = payload.get("email")
            uid = payload.get("uid") or payload.get("user_id") or payload.get("id")
            display_name = payload.get("display_name") or payload.get("displayName") or name
            created_at = (
                payload.get("created_at")
                or payload.get("createdAt")
                or datetime.utcnow().isoformat()
            )

            if not (name and email and uid):
                self._callback_error = "Missing user information"
                self._callback_event.set()
                self.login_failed.emit(self._callback_error)
                return "Missing user information", 400

            self.current_user = User(
                uid=uid,
                username=name,
                email=email,
                display_name=display_name,
                created_at=created_at,
            )
            self.save_session()
            self._callback_error = None
            self._callback_event.set()
            self.login_success.emit(name)
            return "Login successful! You can close this window.", 200

    def start_local_server(self):
        if self._server_thread and self._server_thread.is_alive():
            return

        self._server_thread = threading.Thread(
            target=lambda: self._flask_app.run(
                host="127.0.0.1",
                port=self._port,
                debug=False,
                use_reloader=False,
            )
        )
        self._server_thread.daemon = True
        self._server_thread.start()

    def _web_login_url(self) -> str:
        return _join_url(self._web_app_base_url, self._web_login_path)

    def _web_register_url(self) -> str:
        return _join_url(self._web_app_base_url, self._web_register_path)

    def login(self, timeout: float = 60.0) -> bool:
        if not self._server_thread or not self._server_thread.is_alive():
            self.start_local_server()

        self.current_user = None
        self._callback_error = None
        self._callback_event.clear()

        try:
            webbrowser.open(self._web_login_url())
        except Exception as exc:
            err_msg = f"Unable to open browser: {exc}"
            self.login_failed.emit(err_msg)
            return False

        completed = self._callback_event.wait(timeout)
        if not completed:
            err_msg = "Timed out waiting for the login callback."
            self._callback_error = err_msg
            self.login_failed.emit(err_msg)
            return False

        return self._callback_error is None

    def register(self):
        if not self._server_thread or not self._server_thread.is_alive():
            self.start_local_server()
        webbrowser.open(self._web_register_url())

    def get_current_username(self) -> Optional[str]:
        return self.current_user.username if self.current_user else None

    def save_session(self):
        if self.current_user:
            try:
                with open(self._session_file, "w") as f:
                    json.dump(self.current_user.__dict__, f)
            except Exception as e:
                print(f"Failed to save session: {e}")

    def load_session(self):
        if os.path.exists(self._session_file):
            try:
                with open(self._session_file, "r") as f:
                    data = json.load(f)
                    self.current_user = User(**data)
            except Exception as e:
                print(f"Failed to load session: {e}")
                self.current_user = None

    def logout(self):
        self.current_user = None
        if os.path.exists(self._session_file):
            try:
                os.remove(self._session_file)
            except Exception as e:
                print(f"Failed to remove session: {e}")
