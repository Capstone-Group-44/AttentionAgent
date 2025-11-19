from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox
from PySide6.QtCore import Slot


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

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.check_login)
        # self.timer.start(100)

    @Slot()
    def login(self):
        success = self.viewmodel.login()
        if success:
            name = self.viewmodel.get_current_display_name()
            self.status_label.setText(f"Logged in as {name}")
        else:
            QMessageBox.critical(self, "Login Failed", "Unable to login")

    def check_login(self):
        name = self.viewmodel.get_current_user_name()
        if name:
            self.status_label.setText(f"Logged in as {name}")
            self.timer.stop()  # stop polling after login

    @Slot()
    def register(self):
        self.viewmodel.register()
