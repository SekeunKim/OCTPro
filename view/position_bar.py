from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QColor

class PositionBar(QLabel):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedHeight(10)
        self.setStyleSheet("background-color: #d8dee9; border-radius: 5px;")
        self.position = 0

    def set_position(self, position):
        self.position = position
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        bar_width = self.width()
        marker_x = int(bar_width * self.position)
        painter.setPen(QColor("#5E81AC"))
        painter.setBrush(QColor("#5E81AC"))
        painter.drawRect(marker_x - 2, 0, 4, self.height())

    def mousePressEvent(self, event):
        self.position = event.pos().x() / self.width()
        self.main_window.display_slice_based_on_bar(self.position)
        self.update()