from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QColor, QFont

class SettingsView(QWidget):
    back_requested = Signal()
    logout_requested = Signal()

    def __init__(self, auth_viewmodel=None):
        super().__init__()
        self.auth_viewmodel = auth_viewmodel
        self.setStyleSheet("background-color: #121212;")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Blue Header (Consistent with FocusView) ---
        self.header = QFrame()
        self.header.setStyleSheet("background-color: #1E1E1E; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;")
        self.header.setFixedHeight(120)
        
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 20, 20, 10)
        
        # Top Row (Back Button + Title)
        top_row = QHBoxLayout()
        
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.1); 
                border-radius: 15px; 
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.2);
            }
        """)
        self.back_btn.clicked.connect(self._handle_back)
        top_row.addWidget(self.back_btn)
        
        top_row.addSpacing(10)
        
        title_label = QLabel("Settings")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        top_row.addWidget(title_label)
        
        top_row.addStretch()
        
        header_layout.addLayout(top_row)
        
        self.status_subtitle = QLabel("Manage your profile")
        self.status_subtitle.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")
        self.status_subtitle.setContentsMargins(40, 0, 0, 0) # Align with title
        header_layout.addWidget(self.status_subtitle)
        
        main_layout.addWidget(self.header)
        
        # --- Content Area ---
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Profile Section
        profile_label = QLabel("Profile")
        profile_label.setStyleSheet("font-weight: bold; color: white; font-size: 16px;")
        content_layout.addWidget(profile_label)
        
        # User Info Card
        user_card = QFrame()
        user_card.setStyleSheet("background-color: #1E1E1E; border-radius: 10px; padding: 20px;")
        user_card_layout = QVBoxLayout(user_card)
        
        if self.auth_viewmodel and self.auth_viewmodel.current_user:
            user = self.auth_viewmodel.current_user
            
            # Name
            name_label = QLabel(user.display_name or user.username)
            name_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            user_card_layout.addWidget(name_label)
            
            # Email
            email_label = QLabel(user.email)
            email_label.setStyleSheet("color: #B0B0B0; font-size: 14px;")
            user_card_layout.addWidget(email_label)
        else:
            # Fallback (Shouldn't happen if logged in)
            error_label = QLabel("Not logged in")
            error_label.setStyleSheet("color: #F44336;")
            user_card_layout.addWidget(error_label)
            
        content_layout.addWidget(user_card)
        
        content_layout.addSpacing(30)
        
        # Logout Button
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white; 
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px; 
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.logout_btn.clicked.connect(self._handle_logout)
        content_layout.addWidget(self.logout_btn)
        
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def _handle_back(self):
        self.back_requested.emit()

    def _handle_logout(self):
        if self.auth_viewmodel:
            self.auth_viewmodel.logout()
        self.logout_requested.emit()
