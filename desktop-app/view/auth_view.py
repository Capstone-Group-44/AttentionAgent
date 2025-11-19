from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox
from PySide6.QtCore import Slot, QTimer


class AuthView(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel

        self.setWindowTitle("FocusCam")
        self.setMinimumSize(500, 500)

        # Layouts
        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()

        # Buttons
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout1.addWidget(self.login_button)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        layout1.addWidget(self.register_button)

        layout2.addLayout(layout1)

        # Status label
        self.status_label = QLabel("Not logged in")
        layout2.addWidget(self.status_label)

        self.setLayout(layout2)

        self.viewmodel.login_success.connect(self.on_login_success)
        self.viewmodel.login_failed.connect(self.on_login_failed)

    @Slot()
    def login(self):
        success = self.viewmodel.login()
        if success:
            name = self.viewmodel.get_current_display_name()
            self.status_label.setText(f"Logged in as {name}")
        else:
            QMessageBox.critical(self, "Login Failed", "Unable to login")

    def on_login_success(self, username):
        self.status_label.setText(f"Logged in as {username}")

    def on_login_failed(self, error_message):
        QMessageBox.critical(self, "Login Failed", error_message)

    @Slot()
    def register(self):
        self.viewmodel.register()
