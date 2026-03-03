from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QStackedWidget, QFrame, QDialog, QScrollArea,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QColor, QFont
from view.components.circular_progress import CircularProgressWidget

class ProfileDialog(QDialog):
    def __init__(self, parent=None, auth_viewmodel=None):
        super().__init__(parent)
        self.auth_viewmodel = auth_viewmodel
        self.setWindowTitle("Settings")
        self.setFixedWidth(350)
        self.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")
        
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        close_btn = QPushButton("×")
        close_btn.setStyleSheet("border: none; font-size: 24px; color: #888;")
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        
        # Profile Section
        layout.addSpacing(10)
        profile_label = QLabel("Profile")
        profile_label.setStyleSheet("font-weight: bold; color: white;")
        layout.addWidget(profile_label)
        
        # User Info
        if self.auth_viewmodel and self.auth_viewmodel.current_user:
            user = self.auth_viewmodel.current_user
            
            # Name
            name_label = QLabel(user.display_name or user.username)
            name_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
            layout.addWidget(name_label)
            
            # Email
            email_label = QLabel(user.email)
            email_label.setStyleSheet("color: #B0B0B0; font-size: 14px;")
            layout.addWidget(email_label)
            
            layout.addSpacing(20)
        else:
            # Fallback (Shouldn't happen if logged in)
            error_label = QLabel("Not logged in")
            error_label.setStyleSheet("color: #F44336;")
            layout.addWidget(error_label)
        
        # Logout Button (Real Action)
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white; 
                border-radius: 5px; 
                padding: 10px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        if self.auth_viewmodel:
             logout_btn.clicked.connect(self._handle_logout)
        layout.addWidget(logout_btn)
        
        layout.addStretch()
        self.setLayout(layout)

    def _handle_logout(self):
        if self.auth_viewmodel:
            self.auth_viewmodel.logout()
        self.parent().logout_requested.emit() # Forward signal
        self.close()

class FocusView(QWidget):
    # Signal to notify MainWindow to switch back to AuthView
    logout_requested = Signal()

    def __init__(self, viewmodel, auth_viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.auth_viewmodel = auth_viewmodel
        self.setStyleSheet("background-color: #121212;")
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Blue Header ---
        self.header = QFrame()
        self.header.setStyleSheet("background-color: #1E1E1E; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;")
        self.header.setFixedHeight(120)
        
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 20, 20, 10)
        
        # Top Row (Title + Settings)
        top_row = QHBoxLayout()
        title_label = QLabel("Focus Session")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        top_row.addWidget(title_label)
        
        top_row.addStretch()
        
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet("background-color: rgba(255,255,255,0.3); border-radius: 15px; color: white;")
        top_row.addWidget(self.settings_btn)
        
        header_layout.addLayout(top_row)
        
        self.status_subtitle = QLabel("Ready to focus")
        self.status_subtitle.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")
        header_layout.addWidget(self.status_subtitle)
        
        main_layout.addWidget(self.header)
        
        # --- Content Area (Stacked) ---
        self.content_container = QFrame()
        self.content_container.setStyleSheet(".QFrame { background-color: #1E1E1E; border-radius: 20px; margin: 10px; }")
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        self.content_container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.content_container)
        container_layout.setContentsMargins(20, 40, 20, 40)
        
        self.stack = QStackedWidget()
        self.setup_page = self.create_setup_page()
        self.running_page = self.create_running_page()
        
        self.stack.addWidget(self.setup_page)
        self.stack.addWidget(self.running_page)
        
        container_layout.addWidget(self.stack)
        main_layout.addWidget(self.content_container)
        
        self.setLayout(main_layout)

    def create_setup_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Circular Placeholder
        self.circular_progress_setup = CircularProgressWidget()
        self.circular_progress_setup.set_progress(0)
        self.circular_progress_setup.set_text("25:00")
        self.circular_progress_setup.set_subtext("Focus")
        layout.addWidget(self.circular_progress_setup, alignment=Qt.AlignCenter)
        
        layout.addSpacing(30)
        
        # Start Button
        self.start_btn = QPushButton("Start Focus Session")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285F4; 
                color: white; 
                font-size: 16px; 
                border-radius: 10px; 
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
        """)
        layout.addWidget(self.start_btn)
        
        layout.addSpacing(20)
        
        # Inputs
        self.duration_input = self.create_input_card("Focus Duration (minutes)", "25", icon="🕒")
        layout.addWidget(self.duration_input)
        
        self.break_input = self.create_input_card("Break Duration (minutes)", "5", icon="⚡")
        layout.addWidget(self.break_input)
        
        self.goal_input = self.create_input_card("Daily Session Goal", "6", icon="🎯")
        layout.addWidget(self.goal_input)
        
        page.setLayout(layout)
        return page

    def create_input_card(self, label_text, default_value, icon=""):
        container = QFrame()
        container.setStyleSheet("background-color: #252525; border-radius: 10px;")
        layout = QVBoxLayout(container)
        
        header = QLabel(f"{icon}  {label_text}")
        header.setStyleSheet("color: #B0B0B0; font-weight: bold; font-size: 13px;")
        layout.addWidget(header)
        
        inp = QLineEdit(default_value)
        inp.setStyleSheet("background-color: #2C2C2C; color: white; border: 1px solid #333; border-radius: 5px; padding: 8px;")
        layout.addWidget(inp)
        
        # Store reference to input for later retrieval if needed
        # A bit hacky but simple for now:
        container.input_field = inp 
        
        return container

    def create_running_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Progress Circle
        self.circular_progress = CircularProgressWidget()
        layout.addWidget(self.circular_progress, alignment=Qt.AlignCenter)
        
        layout.addSpacing(40)
        
        # Stop Button
        self.stop_btn = QPushButton("Stop Session")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336; 
                color: white; 
                font-size: 16px; 
                border-radius: 10px; 
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        layout.addWidget(self.stop_btn)
        
        layout.addSpacing(30)
        
        # Stats
        stats_container = QFrame()
        stats_container.setStyleSheet("background-color: #252525; border-radius: 10px; padding: 15px;")
        stats_layout = QHBoxLayout(stats_container)
        
        self.completed_label = QLabel("0 sessions")
        self.completed_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.create_stat_item("Completed", "0 sessions"))
        
        stats_layout.addWidget(self.create_vertical_line())
        
        self.progress_label = QLabel("0%")
        stats_layout.addWidget(self.create_stat_item("Progress", "0%"))
        
        layout.addWidget(stats_container)
        
        page.setLayout(layout)
        return page

    def create_stat_item(self, title, value):
        container = QWidget()
        l = QVBoxLayout(container)
        t = QLabel(title)
        t.setStyleSheet("color: #B0B0B0; font-size: 12px;")
        t.setAlignment(Qt.AlignCenter)
        v = QLabel(value)
        v.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        v.setAlignment(Qt.AlignCenter)
        l.addWidget(t)
        l.addWidget(v)
        return container
        
    def create_vertical_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #DADCE0;")
        return line

    def setup_connections(self):
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.viewmodel.stop_session)
        self.settings_btn.clicked.connect(self.open_settings)
        
        # Live timer update
        self.duration_input.input_field.textChanged.connect(self.on_duration_changed)
        
        self.viewmodel.timer_update.connect(self.update_timer_display)
        self.viewmodel.session_started.connect(self.on_session_started)
        self.viewmodel.session_stopped.connect(self.on_session_stopped)
        
    def on_start_clicked(self):
        try:
            minutes = int(self.duration_input.input_field.text())
            self.viewmodel.start_session(minutes)
        except ValueError:
            # Handle invalid input
            pass

    def open_settings(self):
        dialog = ProfileDialog(self, self.auth_viewmodel)
        dialog.exec()

    def on_duration_changed(self, text):
        if not text:
            self.circular_progress_setup.set_text("00:00")
            return
        
        try:
            mins = int(text)
            self.circular_progress_setup.set_text(f"{mins:02d}:00")
        except ValueError:
            pass # Keep previous or ignore invalid

    def update_timer_display(self, time_str, progress):
        self.circular_progress.set_text(time_str)
        self.circular_progress.set_progress(progress)

    def on_session_started(self):
        self.stack.setCurrentWidget(self.running_page)
        self.status_subtitle.setText("Focus Mode Active")

    def on_session_stopped(self):
        self.stack.setCurrentWidget(self.setup_page)
        self.status_subtitle.setText("Ready to focus")

