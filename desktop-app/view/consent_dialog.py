from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ConsentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Consent for Camera and Gaze Tracking")
        self.setModal(True)
        self.setMinimumSize(760, 640)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #0F1014;
            }
            QFrame#Card {
                background-color: #171922;
                border: 1px solid #2A2B35;
                border-radius: 24px;
            }
            QLabel#Title {
                color: white;
                font-size: 28px;
                font-weight: 800;
            }
            QLabel#Body {
                color: #D4D7E1;
                font-size: 15px;
                line-height: 1.5em;
            }
            QLabel#Section {
                color: white;
                font-size: 16px;
                font-weight: 700;
                margin-top: 8px;
            }
            QPushButton {
                border-radius: 12px;
                font-size: 15px;
                font-weight: 700;
                padding: 14px 20px;
            }
            QPushButton#AcceptButton {
                background-color: #3B82F6;
                color: white;
                border: none;
            }
            QPushButton#AcceptButton:hover {
                background-color: #2563EB;
            }
            QPushButton#DeclineButton {
                background-color: transparent;
                color: #E5E7EB;
                border: 1px solid #3A3D49;
            }
            QPushButton#DeclineButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #11131A;
                width: 10px;
                margin: 4px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #35394A;
                min-height: 24px;
                border-radius: 5px;
            }
            """
        )
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 24)
        card_layout.setSpacing(20)

        title = QLabel("Consent Required")
        title.setObjectName("Title")
        title.setFont(QFont("Inter", 20, QFont.Bold))
        card_layout.addWidget(title)

        intro = QLabel(
            "This application uses your device's camera to estimate your screen "
            "engagement patterns through real-time gaze tracking."
        )
        intro.setObjectName("Body")
        intro.setWordWrap(True)
        card_layout.addWidget(intro)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(14)

        consent_heading = QLabel("With your consent, the system will:")
        consent_heading.setObjectName("Section")
        scroll_layout.addWidget(consent_heading)
        scroll_layout.addWidget(self._body_label("- Access your webcam to detect facial landmarks"))
        scroll_layout.addWidget(
            self._body_label(
                "- Process gaze coordinate data (e.g., where you are looking on the screen)"
            )
        )
        scroll_layout.addWidget(
            self._body_label(
                "- Store session summaries and engagement metrics "
                "(e.g., duration, engagement levels)"
            )
        )

        important_heading = QLabel("Important:")
        important_heading.setObjectName("Section")
        scroll_layout.addWidget(important_heading)
        scroll_layout.addWidget(self._body_label("- No raw video or images are recorded or stored"))
        scroll_layout.addWidget(self._body_label("- All gaze data is processed locally on your device"))
        scroll_layout.addWidget(
            self._body_label("- Only non-identifiable session data is saved for analysis")
        )
        scroll_layout.addWidget(self._body_label("- Your data is not shared with third parties"))

        purpose_heading = QLabel("The purpose of this data collection is to:")
        purpose_heading.setObjectName("Section")
        scroll_layout.addWidget(purpose_heading)
        scroll_layout.addWidget(
            self._body_label("- Provide insights into your screen engagement patterns")
        )
        scroll_layout.addWidget(
            self._body_label(
                "- Help you better understand how you interact with digital content over time"
            )
        )

        closing = QLabel(
            "By selecting Accept, you agree to the collection and use of this data "
            "as described above."
        )
        closing.setObjectName("Body")
        closing.setWordWrap(True)
        scroll_layout.addWidget(closing)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        card_layout.addWidget(scroll_area)

        button_row = QHBoxLayout()
        button_row.addStretch()

        self.decline_button = QPushButton("Decline")
        self.decline_button.setObjectName("DeclineButton")
        self.decline_button.clicked.connect(self.reject)
        button_row.addWidget(self.decline_button)

        self.accept_button = QPushButton("Accept")
        self.accept_button.setObjectName("AcceptButton")
        self.accept_button.clicked.connect(self.accept)
        self.accept_button.setDefault(True)
        button_row.addWidget(self.accept_button)

        card_layout.addLayout(button_row)
        outer_layout.addWidget(card)

    def _body_label(self, text):
        label = QLabel(text)
        label.setObjectName("Body")
        label.setWordWrap(True)
        label.setTextFormat(Qt.PlainText)
        return label
