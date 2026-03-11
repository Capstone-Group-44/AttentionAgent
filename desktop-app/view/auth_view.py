import os
from PySide6.QtWidgets import (QWidget, QPushButton, QLabel, QHBoxLayout, 
                               QVBoxLayout, QMessageBox)
from PySide6.QtCore import Slot, Qt, QSize
from PySide6.QtGui import QIcon, QFont

class AuthView(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel

        self.setWindowTitle("Focus Timer - Login")
        self.setMinimumSize(600, 500)
        
        # Central layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)
        
        # Create Title
        self.title_label = QLabel("Welcome to Focus Timer")
        title_font = QFont("Inter", 26, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: white;")
        
        # Create Subtitle
        self.subtitle_label = QLabel("Track your productivity and stay focused with the\nPomodoro technique")
        subtitle_font = QFont("Inter", 14)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #A0AEC0;")  # Light gray
        
        main_layout.addStretch()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addSpacing(40)
        
        # Paths to icons
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icons_dir = os.path.join(base_dir, "assets", "icons")
        
        # Buttons Layout
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(50, 0, 50, 0)
        
        # Login Button
        self.login_button = QPushButton("  Login")
        self.login_button.setIcon(QIcon(os.path.join(icons_dir, "login.svg")))
        self.login_button.setIconSize(QSize(22, 22))
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setFixedHeight(54)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; 
                color: white; 
                border-radius: 12px; 
                font-size: 16px; 
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        self.login_button.clicked.connect(self.login)
        btn_layout.addWidget(self.login_button)
        
        # Register Button
        self.register_button = QPushButton("  Register")
        self.register_button.setIcon(QIcon(os.path.join(icons_dir, "register.svg")))
        self.register_button.setIconSize(QSize(22, 22))
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setFixedHeight(54)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: white; 
                border: 2px solid #4B5563; 
                border-radius: 12px; 
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                border-color: #6B7280;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.register_button.clicked.connect(self.register)
        btn_layout.addWidget(self.register_button)
        
        main_layout.addLayout(btn_layout)
        main_layout.addSpacing(50)
        
        # Features Section layout
        features_layout = QHBoxLayout()
        features_layout.setAlignment(Qt.AlignCenter)
        features_layout.setSpacing(30)
        
        # Feature 1
        features_layout.addLayout(self.create_feature_col(
            "Focus Sessions", "Customizable timers", 
            os.path.join(icons_dir, "clock.svg"), "rgba(59, 130, 246, 0.15)", "#60a5fa"
        ))
        
        # Feature 2
        features_layout.addLayout(self.create_feature_col(
            "Track Progress", "See your stats", 
            os.path.join(icons_dir, "chart.svg"), "rgba(16, 185, 129, 0.15)", "#34d399"
        ))
        
        # Feature 3
        features_layout.addLayout(self.create_feature_col(
            "Stay Focused", "Break reminders", 
            os.path.join(icons_dir, "zap.svg"), "rgba(167, 139, 250, 0.15)", "#c084fc"
        ))
        
        main_layout.addLayout(features_layout)
        main_layout.addStretch()
        
        self.viewmodel.login_success.connect(self.on_login_success)
        self.viewmodel.login_failed.connect(self.on_login_failed)

    def create_feature_col(self, title, subtitle, icon_path, bg_color, icon_color):
        col_layout = QVBoxLayout()
        col_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        col_layout.setSpacing(8)
        
        # Icon container
        icon_btn = QPushButton()
        icon_btn.setIcon(QIcon(icon_path))
        icon_btn.setIconSize(QSize(28, 28))
        icon_btn.setFixedSize(60, 60)
        icon_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                border-radius: 16px;
            }}
        """)
        
        # Center horizontally
        icon_container = QHBoxLayout()
        icon_container.setAlignment(Qt.AlignCenter)
        icon_container.setContentsMargins(0, 0, 0, 5)
        icon_container.addWidget(icon_btn)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", 13, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Inter", 11))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #9CA3AF;")
        
        col_layout.addLayout(icon_container)
        col_layout.addWidget(title_label)
        col_layout.addWidget(subtitle_label)
        
        return col_layout

    @Slot()
    def login(self):
        self.viewmodel.login()

    def on_login_success(self, username):
        pass

    def on_login_failed(self, error_message):
        QMessageBox.critical(self, "Login Failed", error_message)

    @Slot()
    def register(self):
        self.viewmodel.register()
