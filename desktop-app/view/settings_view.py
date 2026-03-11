from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QColor, QFont, QCursor

from services.notification_service import NotificationService

class SettingsView(QWidget):
    back_requested = Signal()
    logout_requested = Signal()

    def __init__(self, auth_viewmodel=None):
        super().__init__()
        self.auth_viewmodel = auth_viewmodel
        # Use a specific object name to prevent global QLabel cascading if we used type selectors
        self.setObjectName("SettingsViewWidget")
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QWidget#SettingsViewWidget {
                background-color: #0F1014;
            }
        """)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Header ---
        self.header = QFrame()
        self.header.setStyleSheet(".QFrame { background-color: transparent; }")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(40, 40, 40, 20)
        
        title_label = QLabel("Settings")
        title_label.setStyleSheet("color: #FFFFFF; font-size: 32px; font-weight: 800; font-family: 'Inter', sans-serif;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(36, 36)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05); 
                color: #A0A5B5;
                font-size: 18px;
                font-weight: bold;
                border-radius: 18px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: #FFFFFF;
            }
        """)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self._handle_back)
        header_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(self.header)
        
        # --- Content Area ---
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 10, 40, 40)
        content_layout.setSpacing(28)
        
        # --- Profile Section ---
        profile_header_layout = QHBoxLayout()
        profile_header_layout.setSpacing(16)
        
        # Icon circle
        icon_circle = QFrame()
        icon_circle.setFixedSize(56, 56)
        icon_circle.setStyleSheet("""
            .QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3B82F6, stop:1 #2563EB);
                border-radius: 28px;
            }
        """)
        icon_layout = QVBoxLayout(icon_circle)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel("👤")
        # Removing any background styling directly over the widget's content
        icon_label.setStyleSheet("font-size: 28px; color: #FFFFFF; background-color: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        profile_header_layout.addWidget(icon_circle)
        
        profile_label = QLabel("Profile")
        profile_label.setStyleSheet("font-weight: 700; color: #FFFFFF; font-size: 22px; font-family: 'Inter', sans-serif;")
        profile_header_layout.addWidget(profile_label)
        profile_header_layout.addStretch()
        
        content_layout.addLayout(profile_header_layout)
        
        # User Info Card
        user_card = QFrame()
        user_card.setStyleSheet("""
            .QFrame {
                background-color: #1A1B23; 
                border-radius: 16px; 
                border: 1px solid #2A2B35;
            }
        """)
        user_card_layout = QVBoxLayout(user_card)
        user_card_layout.setContentsMargins(24, 24, 24, 24)
        user_card_layout.setSpacing(8)
        
        logged_in_label = QLabel("Logged in as")
        logged_in_label.setStyleSheet("color: #8A8DA0; font-size: 15px; font-weight: 500;")
        user_card_layout.addWidget(logged_in_label)
        
        if self.auth_viewmodel and self.auth_viewmodel.current_user:
            user = self.auth_viewmodel.current_user
            email_label = QLabel(user.email)
            email_label.setStyleSheet("color: #E0E1E6; font-size: 18px; font-weight: 600;")
            user_card_layout.addWidget(email_label)
        else:
             # Fallback
            error_label = QLabel("Not logged in")
            error_label.setStyleSheet("color: #F87171; font-weight: 600;")
            user_card_layout.addWidget(error_label)
            
        content_layout.addWidget(user_card)
        
        # Logout Button
        self.logout_btn = QPushButton("Logout") 
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444; 
                color: #FFFFFF; 
                font-size: 16px;
                font-weight: 700;
                border-radius: 16px; 
                padding: 18px;
                border: none;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)
        self.logout_btn.clicked.connect(self._handle_logout)
        content_layout.addWidget(self.logout_btn)
        
        content_layout.addSpacing(16)
        
        # --- Preferences Section ---
        
        # Separator inside layout
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("border: none; background-color: #2A2B35; max-height: 1px;")
        content_layout.addWidget(separator)
        
        content_layout.addSpacing(16)
        
        preferences_label = QLabel("Preferences")
        preferences_label.setStyleSheet("font-weight: 700; color: #FFFFFF; font-size: 22px; font-family: 'Inter', sans-serif;")
        content_layout.addWidget(preferences_label)
        
        # Notifications Card
        notifications_card = QFrame()
        notifications_card.setStyleSheet("""
            .QFrame {
                background-color: #1A1B23; 
                border-radius: 16px; 
                border: 1px solid #2A2B35;
            }
        """)
        notif_card_layout = QVBoxLayout(notifications_card)
        notif_card_layout.setContentsMargins(24, 24, 24, 24)
        notif_card_layout.setSpacing(8)
        
        notif_title = QLabel("Notifications")
        notif_title.setStyleSheet("color: #E0E1E6; font-size: 18px; font-weight: 600;") 
        notif_card_layout.addWidget(notif_title)
        
        test_notif_btn = QPushButton("Test Notification")
        test_notif_btn.setCursor(Qt.PointingHandCursor)
        test_notif_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6; 
                color: #FFFFFF; 
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px; 
                padding: 10px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        test_notif_btn.clicked.connect(self._handle_test_notification)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(test_notif_btn)
        btn_layout.addStretch()
        
        notif_card_layout.addLayout(btn_layout)

        notif_card_layout.addSpacing(12)

        # --- Distracted Time field ---
        distracted_label = QLabel("Distracted Time (seconds)")
        distracted_label.setStyleSheet("color: #8A8DA0; font-size: 14px; font-weight: 500;")
        notif_card_layout.addWidget(distracted_label)

        self.distracted_time_input = QLineEdit("20")
        self.distracted_time_input.setPlaceholderText("Min 5")
        self.distracted_time_input.setStyleSheet("""
            QLineEdit {
                background-color: #12131A;
                color: #E0E1E6;
                font-size: 14px;
                border: 1px solid #2A2B35;
                border-radius: 8px;
                padding: 10px 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        notif_card_layout.addWidget(self.distracted_time_input)

        notif_card_layout.addSpacing(8)

        # --- Frequency of Notifications field ---
        freq_label = QLabel("Frequency of Notifications (seconds)")
        freq_label.setStyleSheet("color: #8A8DA0; font-size: 14px; font-weight: 500;")
        notif_card_layout.addWidget(freq_label)

        self.notif_freq_input = QLineEdit("60")
        self.notif_freq_input.setPlaceholderText("0 = no cooldown")
        self.notif_freq_input.setStyleSheet("""
            QLineEdit {
                background-color: #12131A;
                color: #E0E1E6;
                font-size: 14px;
                border: 1px solid #2A2B35;
                border-radius: 8px;
                padding: 10px 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        notif_card_layout.addWidget(self.notif_freq_input)

        content_layout.addWidget(notifications_card)
        
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def _handle_back(self):
        self.back_requested.emit()

    def _handle_logout(self):
        if self.auth_viewmodel:
            self.auth_viewmodel.logout()
        self.logout_requested.emit()

    def _handle_test_notification(self):
        NotificationService.send_notification("gazeCam", "User Distracted")

    # ------------------------------------------------------------------
    # Public accessors for distraction notifier settings
    # ------------------------------------------------------------------
    def get_distracted_time_seconds(self) -> int:
        """Return the distracted-time value (min 5, default 20)."""
        try:
            val = int(self.distracted_time_input.text())
            return max(val, 5)
        except (ValueError, AttributeError):
            return 20

    def get_notif_frequency_seconds(self) -> int:
        """Return the notification-frequency value (min 0, default 60)."""
        try:
            val = int(self.notif_freq_input.text())
            return max(val, 0)
        except (ValueError, AttributeError):
            return 60
