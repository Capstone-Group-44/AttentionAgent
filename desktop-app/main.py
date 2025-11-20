import sys
from PySide6.QtWidgets import QApplication
from view.auth_view import AuthView
from viewmodel.auth_viewmodel import AuthViewModel


def main():
    app = QApplication(sys.argv)

    # MVVM setup
    viewmodel = AuthViewModel()
    view = AuthView(viewmodel)
    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
