from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QStackedWidget, QFrame, QDialog, QScrollArea, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QColor, QFont, QImage, QPixmap
import cv2
from view.components.circular_progress import CircularProgressWidget


class FocusView(QWidget):
    # Signal to notify MainWindow to switch back to AuthView
    logout_requested = Signal()
    # Signal to notify MainWindow to switch to SettingsView
    settings_requested = Signal()

    def __init__(self, viewmodel, auth_viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.auth_viewmodel = auth_viewmodel
        self.setObjectName("FocusViewWidget")
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QWidget#FocusViewWidget {
                background-color: #0F1014;
            }
        """)
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header ---
        self.header = QFrame()
        self.header.setStyleSheet(
            ".QFrame { background-color: transparent; border: none; }")
        self.header.setFixedHeight(120)

        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 20, 20, 10)

        # Top Row (Title + Settings)
        top_row = QHBoxLayout()
        self.welcome_label = QLabel("Welcome back!")
        self.welcome_label.setStyleSheet(
            "color: white; font-size: 26px; font-weight: 800; font-family: 'Inter', sans-serif;")
        top_row.addWidget(self.welcome_label)

        top_row.addStretch()

        self.settings_btn = QPushButton("⚙")
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
        top_row.addWidget(self.settings_btn)

        header_layout.addLayout(top_row)

        self.status_subtitle = QLabel("Ready to start session")
        self.status_subtitle.setStyleSheet(
            "color: rgba(255,255,255,0.8); font-size: 14px;")
        header_layout.addWidget(self.status_subtitle)

        main_layout.addWidget(self.header)

        # Set greeting text
        if self.auth_viewmodel and self.auth_viewmodel.current_user:
            user = self.auth_viewmodel.current_user
            name = user.display_name or user.username
            self.welcome_label.setText(f"Welcome back, {name}!")

        # --- Content Area (Stacked) ---
        self.content_container = QFrame()
        self.content_container.setStyleSheet(
            ".QFrame { background-color: transparent; border: none; }")

        container_layout = QVBoxLayout(self.content_container)
        container_layout.setContentsMargins(20, 20, 20, 40)

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
        layout = QHBoxLayout()  # Horizontal main layout
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

        self.circular_progress_setup = CircularProgressWidget()
        self.circular_progress_setup.set_progress(0)
        self.circular_progress_setup.set_text("25:00")
        self.circular_progress_setup.set_subtext("Focus")
        left_col.addWidget(self.circular_progress_setup,
                           alignment=Qt.AlignCenter)

        layout.addWidget(left_panel_setup, stretch=1)  # 50% width

        # --- Right Column: Controls ---
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignTop)
        right_col.setSpacing(24)

        # Start Button
        self.start_btn = QPushButton("Start Session")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
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
        self.task_input = self.create_stacked_input_card(
            "Task Name", "What are you working on?")
        right_col.addWidget(self.task_input)

        # Duration Inputs Row
        durations_row = QHBoxLayout()
        durations_row.setSpacing(16)

        self.duration_input = self.create_stacked_input_card(
            "Session (min)", "25")
        durations_row.addWidget(self.duration_input)

        self.short_break_input = self.create_stacked_input_card(
            "Short Break", "5")
        durations_row.addWidget(self.short_break_input)

        self.long_break_input = self.create_stacked_input_card(
            "Long Break", "15")
        durations_row.addWidget(self.long_break_input)

        right_col.addLayout(durations_row)

        layout.addLayout(right_col, stretch=1)  # 50% width

        page.setLayout(layout)
        return page

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
        header.setStyleSheet(
            "color: #E0E1E6; font-weight: 600; font-size: 13px;")
        layout.addWidget(header)

        inp = QLineEdit()
        # If it's a number, use as text. If not, treat as placeholder text.
        if default_value_or_placeholder.isdigit():
            inp.setText(default_value_or_placeholder)
            inp.setAlignment(Qt.AlignCenter)
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
        return container

    def create_running_page(self):
        page = QWidget()
        layout = QHBoxLayout()  # Horizontal main layout
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

        # Camera Feed
        self.camera_feed_label = QLabel("Camera Output")
        self.camera_feed_label.setAlignment(Qt.AlignCenter)
        self.camera_feed_label.setStyleSheet("""
            QLabel {
                background-color: #050608;
                border-radius: 12px;
                border: 1px solid #2A2B35;
                color: #A0A5B5;
            }
        """)
        self.camera_feed_label.setMinimumHeight(240)
        right_col.addWidget(self.camera_feed_label)

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

        # Stop Button
        self.stop_btn = QPushButton("Stop Session")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
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

        self.completed_label = QLabel("0 sessions")
        self.completed_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(
            self.create_stat_item("Completed", "0 sessions"))

        stats_layout.addWidget(self.create_vertical_line())

        self.progress_label = QLabel("0%")
        stats_layout.addWidget(self.create_stat_item("Progress", "0%"))

        right_col.addWidget(stats_container)

        layout.addLayout(right_col, stretch=1)

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
        line.setStyleSheet("border: none; background-color: #2A2B35;")
        line.setMaximumWidth(1)
        return line

    def setup_connections(self):
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.viewmodel.stop_session)
        self.short_break_btn.clicked.connect(self.on_short_break_clicked)
        self.long_break_btn.clicked.connect(self.on_long_break_clicked)
        self.settings_btn.clicked.connect(self.open_settings)

        # Live timer update
        self.duration_input.input_field.textChanged.connect(
            self.on_duration_changed)

        self.viewmodel.timer_update.connect(self.update_timer_display)
        self.viewmodel.session_started.connect(self.on_session_started)
        self.viewmodel.session_stopped.connect(self.on_session_stopped)
        self.viewmodel.break_started.connect(self.on_break_started)
        self.viewmodel.focus_resumed.connect(self.on_focus_resumed)
        self.viewmodel.frame_ready.connect(self.update_camera_feed)

    def on_start_clicked(self):
        try:
            minutes = int(self.duration_input.input_field.text())
            self.viewmodel.start_session(minutes)
        except ValueError:
            # Handle invalid input
            pass

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

    def on_duration_changed(self, text):
        if not text:
            self.circular_progress_setup.set_text("00:00")
            return

        try:
            mins = int(text)
            self.circular_progress_setup.set_text(f"{mins:02d}:00")
        except ValueError:
            pass  # Keep previous or ignore invalid

    def update_timer_display(self, time_str, progress):
        self.circular_progress.set_text(time_str)
        self.circular_progress.set_progress(progress)

    def update_camera_feed(self, frame):
        # Frame is BGR numpy array from opencv
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        # Scale pixmap to fit the label while keeping aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.camera_feed_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.camera_feed_label.setPixmap(scaled_pixmap)

    def on_session_started(self):
        self.stack.setCurrentWidget(self.running_page)
        self.status_subtitle.setText("Session Active")
        self.short_break_btn.setEnabled(True)
        self.long_break_btn.setEnabled(True)
        self.circular_progress.set_subtext("Focus")
        self.camera_feed_label.setText("Waiting for camera...")

    def on_session_stopped(self):
        self.stack.setCurrentWidget(self.setup_page)
        self.status_subtitle.setText("Ready to start session")
        self.camera_feed_label.clear()
        self.camera_feed_label.setText("Camera Output")

    def on_break_started(self, break_name):
        self.status_subtitle.setText(f"{break_name} Active")
        self.short_break_btn.setEnabled(False)
        self.long_break_btn.setEnabled(False)
        self.circular_progress.set_subtext("Break")

    def on_focus_resumed(self):
        self.status_subtitle.setText("Session Active")
        self.short_break_btn.setEnabled(True)
        self.long_break_btn.setEnabled(True)
        self.circular_progress.set_subtext("Focus")
