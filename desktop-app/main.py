import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from view.auth_view import AuthView
from viewmodel.auth_viewmodel import AuthViewModel
from view.focus_view import FocusView
from viewmodel.focus_viewmodel import FocusViewModel
<<<<<<< HEAD
=======
from view.settings_view import SettingsView
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FocusCam")
        
        # MVVM setup
        self.auth_viewmodel = AuthViewModel()
        self.auth_view = AuthView(self.auth_viewmodel)
        
<<<<<<< HEAD
        self.focus_viewmodel = FocusViewModel(self.auth_viewmodel)
=======
        self.focus_viewmodel = FocusViewModel()
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        self.focus_view = FocusView(self.focus_viewmodel, self.auth_viewmodel)

        # Navigation setup
        self.stacked_widget = QStackedWidget()
        
        self.settings_view = SettingsView(self.auth_viewmodel)
        
        self.stacked_widget.addWidget(self.auth_view)
        self.stacked_widget.addWidget(self.focus_view)
<<<<<<< HEAD
=======
        self.stacked_widget.addWidget(self.settings_view)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
        self.setCentralWidget(self.stacked_widget)
        
        # Connect signals
        self.auth_viewmodel.login_success.connect(self.show_focus_view)
<<<<<<< HEAD
        self.focus_view.logout_requested.connect(self.handle_logout)
=======
        
        # FocusView signals
        self.focus_view.logout_requested.connect(self.handle_logout)
        self.focus_view.settings_requested.connect(self.show_settings_view)
        
        # SettingsView signals
        self.settings_view.back_requested.connect(self.show_focus_view)
        self.settings_view.logout_requested.connect(self.handle_logout)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728

        # Auto-login if session exists
        if self.auth_viewmodel.current_user:
            self.show_focus_view()

    def show_focus_view(self):
        self.stacked_widget.setCurrentWidget(self.focus_view)
<<<<<<< HEAD

    def handle_logout(self):
        # AuthViewModel logout is already called in ProfileDialog, 
        # but good to ensure UI state consistency here if needed.
=======

    def show_settings_view(self):
        self.stacked_widget.setCurrentWidget(self.settings_view)

    def handle_logout(self):
        # AuthViewModel logout is handled by SettingsView now.
        # Ensure UI state consistency here if needed.
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        self.stacked_widget.setCurrentWidget(self.auth_view)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
