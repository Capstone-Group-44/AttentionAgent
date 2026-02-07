from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QBrush

class CircularProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0  # 0 to 100
        self._text = "00:00"
        self._subtext = "Focus"
        self.setMinimumSize(200, 200)

    def set_progress(self, value):
        self._progress = value
        self.update()

    def set_text(self, text):
        self._text = text
        self.update()
        
    def set_subtext(self, text):
        self._subtext = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)
        
        # Center the coordinate system
        painter.translate(width / 2, height / 2)
        painter.scale(side / 200.0, side / 200.0)

        # Draw background circle
        pen = QPen(QColor("#333333"))  # Dark Grey Track
        pen.setWidth(10)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(-80, -80, 160, 160)

        # Draw progress arc
        pen.setColor(QColor("#4285F4"))  # Google Blue-ish (Keep accent)
        painter.setPen(pen)
        
        # Qt draws angles in 1/16th of a degree. 
        # Start at 90 degrees (top), go counter-clockwise (positive span) or clockwise (negative span).
        # Typically progress bars start at top and go clockwise. 
        # 0 deg is 3 o'clock. 90 deg is 12 o'clock.
        startAngle = 90 * 16
        spanAngle = -self._progress * 3.6 * 16
        
        painter.drawArc(-80, -80, 160, 160, startAngle, spanAngle)
        
        # Draw text
        painter.setPen(Qt.white)  # White text for dark mode
        font = QFont()
        font.setPixelSize(32)
        font.setBold(True)
        painter.setFont(font)
        
        text_rect = QRectF(-70, -30, 140, 40)
        painter.drawText(text_rect, Qt.AlignCenter, self._text)
        
        font.setPixelSize(14)
        font.setBold(False)
        painter.setFont(font)
        subtext_rect = QRectF(-70, 10, 140, 30)
        painter.setPen(QColor("#B0B0B0"))  # Light grey subtext
        painter.drawText(subtext_rect, Qt.AlignCenter, self._subtext)
