# sagittal_view.py
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen

class SagittalView(QLabel):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setStyleSheet("background-color: #777F86; border: 1px solid #4C566A;")
        self.sagittal_image = None  # Holds the sagittal image if loaded

    def set_sagittal_image(self, image):
        self.sagittal_image = QPixmap.fromImage(image)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        # Draw the sagittal image if available
        if self.sagittal_image:
            painter.drawPixmap(self.rect(), self.sagittal_image)

        # Draw a white line at the current slice position
        if self.main_window.dicom_data is not None:
            num_slices = self.main_window.dicom_data.shape[0]-1
            line_x = int((self.main_window.current_slice / num_slices) * self.width())
            painter.setPen(QPen(QColor("white"), 1))
            painter.drawLine(line_x, 0, line_x, self.height())