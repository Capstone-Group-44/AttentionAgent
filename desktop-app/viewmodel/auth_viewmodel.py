import webbrowser
import time
from model.user import User


class AuthViewModel:
    def __init__(self):
        self.current_user = None

    def login(self):
        webbrowser.open("#")  # URL to the webapp login page

        time.sleep(2)  # Wait for user to complete login in browser

        # missing API polling endpoint so user can be assigned

        return True

    def register(self):
        webbrowser.open("#")

    def get_current_display_name(self):
        if self.current_user:
            return self.current_user.display_name
        return None
