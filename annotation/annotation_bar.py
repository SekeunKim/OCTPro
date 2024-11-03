from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QColor, QFont

class AnnotationBar(QLabel):
    def __init__(self, label_index, main_window, parent=None):
        super().__init__(parent)
        self.label_index = label_index
        self.main_window = main_window
        self.setFixedHeight(20)
        self.setStyleSheet("background-color: #f0f2f5; border-radius: 5px;")
        
        # Dictionary to store annotations per frame
        self.annotations_per_frame = {}  # {frame_index: [(start_x, end_x, color), ...]}
        self.current_frame = 0

    def update_annotations_for_frame(self, frame_index):
        """Update annotations for the given frame index."""
        self.current_frame = frame_index
        self.update()  # Trigger a repaint to show annotations for the current frame

    def add_annotation(self, start_x, end_x, color):
        """Add a new annotation for the current frame."""
        if self.current_frame not in self.annotations_per_frame:
            self.annotations_per_frame[self.current_frame] = []
        self.annotations_per_frame[self.current_frame].append((start_x, end_x, color))
        self.update()

    def mousePressEvent(self, event):
        click_pos = event.pos().x()
        self.dragging = False
        self.resizing = False
        self.current_annotation = None
        self.resize_handle = None

        # Get current frame's annotations
        frame_annotations = self.annotations_per_frame.setdefault(self.current_frame, [])
        for i, (start_x, end_x, color) in enumerate(frame_annotations):
            if start_x - 2 <= click_pos <= start_x + 2:
                self.resizing = True
                self.resize_handle = 'left'
                self.current_annotation = i
                break
            elif end_x - 2 <= click_pos <= end_x + 2:
                self.resizing = True
                self.resize_handle = 'right'
                self.current_annotation = i
                break
            elif start_x <= click_pos <= end_x:
                self.dragging = True
                self.current_annotation = i
                break

        if not self.resizing and not self.dragging:
            color = QColor("#5E81AC") if self.label_index == 0 else QColor("#88C0D0") if self.label_index == 1 else \
                    QColor("#EBCB8B") if self.label_index == 2 else QColor("#BF616A")
            frame_annotations.append([click_pos, click_pos, color])
            self.current_annotation = len(frame_annotations) - 1
            self.dragging = True
        self.update()

    def mouseMoveEvent(self, event):
        if self.current_annotation is None:
            return
        current_pos = event.pos().x()

        frame_annotations = self.annotations_per_frame[self.current_frame]
        if self.resizing and self.resize_handle:
            if self.resize_handle == 'left':
                frame_annotations[self.current_annotation][0] = current_pos
            elif self.resize_handle == 'right':
                frame_annotations[self.current_annotation][1] = current_pos
        elif self.dragging:
            frame_annotations[self.current_annotation][1] = current_pos

        self.main_window.display_slice_based_on_bar(current_pos / self.width())
        self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.current_annotation = None
        self.resize_handle = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        # Draw only annotations for the current frame
        frame_annotations = self.annotations_per_frame.get(self.current_frame, [])
        for start_x, end_x, color in frame_annotations:
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawRect(start_x, 0, end_x - start_x, self.height())
            
            # Draw resize handles
            handle_color = QColor("#4C8FBF")
            painter.setPen(handle_color)
            painter.setBrush(handle_color)
            painter.drawRect(start_x - 2, 0, 4, self.height())
            painter.drawRect(end_x - 2, 0, 4, self.height())

        # Draw labels 'P' and 'D' at the left and right sides
        painter.setPen(QColor("#4C566A"))
        font = QFont()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(5, self.height() - 5, "P")
        painter.drawText(self.width() - 15, self.height() - 5, "D")