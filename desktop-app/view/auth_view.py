from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QMessageBox
from PySide6.QtCore import Slot


class AuthView(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel

        self.setWindowTitle("FocusCam")
        self.setMinimumSize(300, 200)

        # Layout
        layout = QVBoxLayout()

        # Buttons
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        # Status label
        self.status_label = QLabel("Not logged in")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    @Slot()
    def login(self):
        success = self.viewmodel.login()
        if success:
            name = self.viewmodel.get_current_display_name()
            self.status_label.setText(f"Logged in as {name}")
        else:
            QMessageBox.critical(self, "Login Failed", "Unable to login")

    @Slot()
    def register(self):
        self.viewmodel.register()
