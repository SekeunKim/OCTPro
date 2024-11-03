from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtCore import Signal

class FileExplorer(QWidget):
    file_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.file_dialog = QFileDialog(self)
        self.file_dialog.setNameFilter("DICOM Files (*.dcm);;All Files (*)")
        self.file_dialog.fileSelected.connect(self.file_selected.emit)

    def open_file_dialog(self):
        self.file_dialog.exec_()