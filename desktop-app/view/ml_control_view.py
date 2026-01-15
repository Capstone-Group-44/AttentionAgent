from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Slot, Signal

class MLControlView(QWidget):
    logout_requested = Signal()

    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        
        self.setWindowTitle("ML Control")
        self.setMinimumSize(500, 500)
        
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Status Label
        self.status_label = QLabel("ML Algorithm: Stopped")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start ML Algorithm")
        self.start_button.setMinimumHeight(50)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop ML Algorithm")
        self.stop_button.setMinimumHeight(50)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        layout.addSpacing(20)
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("background-color: #f44336; color: white;")
        layout.addWidget(self.logout_button)
        
        layout.addStretch()
        
        self.setLayout(layout)

    def setup_connections(self):
        self.start_button.clicked.connect(self.viewmodel.start_ml_script)
        self.stop_button.clicked.connect(self.viewmodel.stop_ml_script)
        self.logout_button.clicked.connect(self.logout_requested.emit)
        
        self.viewmodel.is_running_changed.connect(self.on_running_changed)
        self.viewmodel.error_occurred.connect(self.on_error)

    @Slot(bool)
    def on_running_changed(self, is_running):
        if is_running:
            self.status_label.setText("ML Algorithm: Running")
            self.status_label.setStyleSheet("color: green; font-size: 18px; font-weight: bold;")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.status_label.setText("ML Algorithm: Stopped")
            self.status_label.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    @Slot(str)
    def on_error(self, message):
        QMessageBox.critical(self, "Error", message)
