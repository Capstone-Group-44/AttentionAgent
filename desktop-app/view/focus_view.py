from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
<<<<<<< HEAD
    QLineEdit, QStackedWidget, QFrame, QDialog, QScrollArea, QMessageBox,
=======
    QLineEdit, QStackedWidget, QFrame, QDialog, QScrollArea,
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QColor, QFont
from view.components.circular_progress import CircularProgressWidget

<<<<<<< HEAD
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
=======
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728

class FocusView(QWidget):
    # Signal to notify MainWindow to switch back to AuthView
    logout_requested = Signal()
<<<<<<< HEAD
=======
    # Signal to notify MainWindow to switch to SettingsView
    settings_requested = Signal()
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728

    def __init__(self, viewmodel, auth_viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.auth_viewmodel = auth_viewmodel
<<<<<<< HEAD
        self.setStyleSheet("background-color: #121212;")
=======
        self.setObjectName("FocusViewWidget")
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QWidget#FocusViewWidget {
                background-color: #0F1014;
            }
        """)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
<<<<<<< HEAD
        # --- Blue Header ---
        self.header = QFrame()
        self.header.setStyleSheet("background-color: #1E1E1E; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;")
=======
        # --- Header ---
        self.header = QFrame()
        self.header.setStyleSheet(".QFrame { background-color: transparent; border: none; }")
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        self.header.setFixedHeight(120)
        
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 20, 20, 10)
        
        # Top Row (Title + Settings)
        top_row = QHBoxLayout()
<<<<<<< HEAD
        title_label = QLabel("Focus Session")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        top_row.addWidget(title_label)
=======
        self.welcome_label = QLabel("Welcome back!")
        self.welcome_label.setStyleSheet("color: white; font-size: 26px; font-weight: 800; font-family: 'Inter', sans-serif;")
        top_row.addWidget(self.welcome_label)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
        top_row.addStretch()
        
        self.settings_btn = QPushButton("⚙")
<<<<<<< HEAD
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet("background-color: rgba(255,255,255,0.3); border-radius: 15px; color: white;")
=======
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05); 
                color: #A0A5B5;
                font-size: 18px;
                border-radius: 18px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
            }
        """)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        top_row.addWidget(self.settings_btn)
        
        header_layout.addLayout(top_row)
        
        self.status_subtitle = QLabel("Ready to focus")
        self.status_subtitle.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")
        header_layout.addWidget(self.status_subtitle)
        
        main_layout.addWidget(self.header)
        
<<<<<<< HEAD
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
=======
        # Set greeting text
        if self.auth_viewmodel and self.auth_viewmodel.current_user:
            user = self.auth_viewmodel.current_user
            name = user.display_name or user.username
            self.welcome_label.setText(f"Welcome back, {name}!")

        # --- Content Area (Stacked) ---
        self.content_container = QFrame()
        self.content_container.setStyleSheet(".QFrame { background-color: transparent; border: none; }")
        
        container_layout = QVBoxLayout(self.content_container)
        container_layout.setContentsMargins(20, 20, 20, 40)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
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
<<<<<<< HEAD
        layout = QVBoxLayout()
        
        # Circular Placeholder
=======
        layout = QHBoxLayout() # Horizontal main layout
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Left Column: Timer ---
        left_panel_setup = QFrame()
        left_panel_setup.setStyleSheet("""
            .QFrame {
                background-color: #050608;
                border-radius: 24px;
            }
        """)
        left_col = QVBoxLayout(left_panel_setup)
        
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        self.circular_progress_setup = CircularProgressWidget()
        self.circular_progress_setup.set_progress(0)
        self.circular_progress_setup.set_text("25:00")
        self.circular_progress_setup.set_subtext("Focus")
<<<<<<< HEAD
        layout.addWidget(self.circular_progress_setup, alignment=Qt.AlignCenter)
        
        layout.addSpacing(30)
=======
        left_col.addWidget(self.circular_progress_setup, alignment=Qt.AlignCenter)
        
        layout.addWidget(left_panel_setup, stretch=1) # 50% width

        # --- Right Column: Controls ---
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignTop)
        right_col.setSpacing(24)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
        # Start Button
        self.start_btn = QPushButton("Start Focus Session")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
<<<<<<< HEAD
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
=======
                background-color: #3B82F6; 
                color: white; 
                font-size: 16px; 
                font-weight: 700;
                border-radius: 12px; 
                padding: 18px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        right_col.addWidget(self.start_btn)
        
        # Task Name Input
        self.task_input = self.create_stacked_input_card("Task Name", "What are you working on?")
        right_col.addWidget(self.task_input)
        
        # Duration Inputs Row
        durations_row = QHBoxLayout()
        durations_row.setSpacing(16)
        
        self.duration_input = self.create_stacked_input_card("Focus (min)", "25")
        durations_row.addWidget(self.duration_input)
        
        self.short_break_input = self.create_stacked_input_card("Short Break", "5")
        durations_row.addWidget(self.short_break_input)
        
        self.long_break_input = self.create_stacked_input_card("Long Break", "15")
        durations_row.addWidget(self.long_break_input)
        
        right_col.addLayout(durations_row)
        
        layout.addLayout(right_col, stretch=1) # 50% width
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
        page.setLayout(layout)
        return page

<<<<<<< HEAD
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
        
=======
    def create_stacked_input_card(self, label_text, default_value_or_placeholder):
        """Creates a card with a label stacked above an input field."""
        container = QFrame()
        container.setStyleSheet("""
            .QFrame {
                background-color: #1A1B23; 
                border-radius: 12px; 
                border: 1px solid #2A2B35;
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        header = QLabel(label_text)
        header.setStyleSheet("color: #E0E1E6; font-weight: 600; font-size: 13px;")
        layout.addWidget(header)
        
        inp = QLineEdit()
        # If it's a number, use as text. If not, treat as placeholder text.
        if default_value_or_placeholder.isdigit():
            inp.setText(default_value_or_placeholder)
        else:
            inp.setPlaceholderText(default_value_or_placeholder)
            
        inp.setStyleSheet("""
            QLineEdit {
                background-color: #0F1014; 
                color: white; 
                border: 1px solid #2A2B35; 
                border-radius: 8px; 
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        layout.addWidget(inp)
        
        container.input_field = inp 
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        return container

    def create_running_page(self):
        page = QWidget()
<<<<<<< HEAD
        layout = QVBoxLayout()
        
        # Progress Circle
        self.circular_progress = CircularProgressWidget()
        layout.addWidget(self.circular_progress, alignment=Qt.AlignCenter)
        
        layout.addSpacing(40)
=======
        layout = QHBoxLayout() # Horizontal main layout
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Left Column: Timer ---
        left_panel_running = QFrame()
        left_panel_running.setStyleSheet("""
            .QFrame {
                background-color: #050608;
                border-radius: 24px;
            }
        """)
        left_col = QVBoxLayout(left_panel_running)
        self.circular_progress = CircularProgressWidget()
        left_col.addWidget(self.circular_progress, alignment=Qt.AlignCenter)
        layout.addWidget(left_panel_running, stretch=1)
        
        # --- Right Column: Controls and Stats ---
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignTop)
        right_col.setSpacing(24)
        
        # Action Buttons Layout
        action_btns_layout = QVBoxLayout()
        action_btns_layout.setSpacing(12)
        
        # Row 1: Break Buttons
        break_btns_layout = QHBoxLayout()
        break_btns_layout.setSpacing(12)
        
        button_style = """
            QPushButton {
                background-color: #1A1B23; 
                color: #A0A5B5; 
                font-size: 15px; 
                font-weight: 700;
                border-radius: 12px; 
                padding: 16px;
                border: 1px solid #2A2B35;
            }
            QPushButton:hover {
                background-color: #2A2B35;
                color: white;
            }
            QPushButton:pressed {
                background-color: #3B82F6;
                color: white;
            }
            QPushButton:disabled {
                background-color: #0F1014;
                color: #4A4D5E;
                border: 1px solid #1A1B23;
            }
        """
        
        self.short_break_btn = QPushButton("Short Break")
        self.short_break_btn.setCursor(Qt.PointingHandCursor)
        self.short_break_btn.setStyleSheet(button_style)
        break_btns_layout.addWidget(self.short_break_btn, stretch=1)
        
        self.long_break_btn = QPushButton("Long Break")
        self.long_break_btn.setCursor(Qt.PointingHandCursor)
        self.long_break_btn.setStyleSheet(button_style)
        break_btns_layout.addWidget(self.long_break_btn, stretch=1)
        
        action_btns_layout.addLayout(break_btns_layout)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
        # Stop Button
        self.stop_btn = QPushButton("Stop Session")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
<<<<<<< HEAD
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
=======
                background-color: #EF4444; 
                color: white; 
                font-size: 16px; 
                font-weight: 700;
                border-radius: 12px; 
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
        action_btns_layout.addWidget(self.stop_btn)
        
        right_col.addLayout(action_btns_layout)
        
        # Stats
        stats_container = QFrame()
        stats_container.setStyleSheet("""
            .QFrame {
                background-color: #1A1B23; 
                border-radius: 12px; 
                border: 1px solid #2A2B35;
            }
        """)
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(20, 20, 20, 20)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
        self.completed_label = QLabel("0 sessions")
        self.completed_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.create_stat_item("Completed", "0 sessions"))
        
        stats_layout.addWidget(self.create_vertical_line())
        
        self.progress_label = QLabel("0%")
        stats_layout.addWidget(self.create_stat_item("Progress", "0%"))
        
<<<<<<< HEAD
        layout.addWidget(stats_container)
=======
        right_col.addWidget(stats_container)
        
        layout.addLayout(right_col, stretch=1)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
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
<<<<<<< HEAD
        line.setStyleSheet("color: #DADCE0;")
=======
        line.setStyleSheet("border: none; background-color: #2A2B35;")
        line.setMaximumWidth(1)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        return line

    def setup_connections(self):
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.viewmodel.stop_session)
<<<<<<< HEAD
=======
        self.short_break_btn.clicked.connect(self.on_short_break_clicked)
        self.long_break_btn.clicked.connect(self.on_long_break_clicked)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        self.settings_btn.clicked.connect(self.open_settings)
        
        # Live timer update
        self.duration_input.input_field.textChanged.connect(self.on_duration_changed)
        
        self.viewmodel.timer_update.connect(self.update_timer_display)
        self.viewmodel.session_started.connect(self.on_session_started)
        self.viewmodel.session_stopped.connect(self.on_session_stopped)
<<<<<<< HEAD
        self.viewmodel.error_occurred.connect(self.on_error)
=======
        self.viewmodel.break_started.connect(self.on_break_started)
        self.viewmodel.focus_resumed.connect(self.on_focus_resumed)
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728
        
    def on_start_clicked(self):
        try:
            minutes = int(self.duration_input.input_field.text())
            self.viewmodel.start_session(minutes)
        except ValueError:
            # Handle invalid input
            pass

<<<<<<< HEAD
    def open_settings(self):
        dialog = ProfileDialog(self, self.auth_viewmodel)
        dialog.exec()
=======
    def on_short_break_clicked(self):
        try:
            minutes = int(self.short_break_input.input_field.text())
            self.viewmodel.start_break(minutes, "Short Break")
        except ValueError:
            pass

    def on_long_break_clicked(self):
        try:
            minutes = int(self.long_break_input.input_field.text())
            self.viewmodel.start_break(minutes, "Long Break")
        except ValueError:
            pass

    def open_settings(self):
        self.settings_requested.emit()
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728

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
<<<<<<< HEAD
=======
        self.short_break_btn.setEnabled(True)
        self.long_break_btn.setEnabled(True)
        self.circular_progress.set_subtext("Focus")
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728

    def on_session_stopped(self):
        self.stack.setCurrentWidget(self.setup_page)
        self.status_subtitle.setText("Ready to focus")

<<<<<<< HEAD
    def on_error(self, message):
        QMessageBox.critical(self, "Focus Session Error", message)
=======
    def on_break_started(self, break_name):
        self.status_subtitle.setText(f"{break_name} Active")
        self.short_break_btn.setEnabled(False)
        self.long_break_btn.setEnabled(False)
        self.circular_progress.set_subtext("Break")
        
    def on_focus_resumed(self):
        self.status_subtitle.setText("Focus Mode Active")
        self.short_break_btn.setEnabled(True)
        self.long_break_btn.setEnabled(True)
        self.circular_progress.set_subtext("Focus")
>>>>>>> c321198154d8cbc24e6ee881882d39c335ba3728

