import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from view.auth_view import AuthView
from viewmodel.auth_viewmodel import AuthViewModel
from view.ml_control_view import MLControlView
from viewmodel.ml_control_viewmodel import MLControlViewModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FocusCam")
        
        # MVVM setup
        self.auth_viewmodel = AuthViewModel()
        self.auth_view = AuthView(self.auth_viewmodel)
        
        self.ml_viewmodel = MLControlViewModel()
        self.ml_view = MLControlView(self.ml_viewmodel)

        # Navigation setup
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.auth_view)
        self.stacked_widget.addWidget(self.ml_view)
        
        self.setCentralWidget(self.stacked_widget)
        
        # Connect signals
        self.auth_viewmodel.login_success.connect(self.show_ml_control)
        self.ml_view.logout_requested.connect(self.handle_logout)

        # Auto-login if session exists
        if self.auth_viewmodel.current_user:
            self.show_ml_control()

    def show_ml_control(self):
        self.stacked_widget.setCurrentWidget(self.ml_view)

    def handle_logout(self):
        self.auth_viewmodel.logout()
        self.stacked_widget.setCurrentWidget(self.auth_view)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
