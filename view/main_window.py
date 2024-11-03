# OCTPro
# Copyright (c) 2024 Sekun Kim
# All rights reserved.
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QStatusBar, QFileDialog
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import numpy as np
import pydicom
import os
import json
from view.file_explorer import FileExplorer
from annotation.annotation_bar import AnnotationBar
from view.position_bar import PositionBar
from view.sagittal_view import SagittalView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Display copyright message
        self.setWindowTitle("OCTPro © 2024 Sekun Kim")
        
        # Set window properties
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
        self.current_slice = 0
        self.dicom_data = None
        self.dicom_file_path = None 

        # Set the background color for the main window
        self.setStyleSheet("background-color: #777F86;")

        # Initialize the annotation bars list
        self.annotation_bars = []


    def init_ui(self):
        main_layout = QVBoxLayout()
        axial_layout = QVBoxLayout()
        sagittal_layout = QVBoxLayout()
        annotation_layout = QVBoxLayout()

        self.file_explorer = FileExplorer(self)
        self.file_explorer.file_selected.connect(self.load_dicom)

        open_button = QPushButton("Open DICOM File")
        open_button.clicked.connect(self.file_explorer.open_file_dialog)
        open_button.setStyleSheet("background-color: #2E3440; color: white; border-radius: 5px; padding: 5px;")

        # Export button setup
        export_button = QPushButton("Export Annotations")
        export_button.clicked.connect(self.export_annotations)
        export_button.setStyleSheet("background-color: #2E3440; color: white; border-radius: 5px; padding: 5px;")

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #777F86; border: 1px solid gray;")
        self.image_label.setScaledContents(True)

        self.frame_indicator = QLabel()
        self.frame_indicator.setAlignment(Qt.AlignCenter)
        self.frame_indicator.setStyleSheet("color: white; font-size: 14px;")

        self.sagittal_label = SagittalView(self)
        axial_layout.addWidget(self.image_label)
        axial_layout.addWidget(self.frame_indicator)
        sagittal_layout.addWidget(self.sagittal_label)

        main_layout.addWidget(open_button)
        main_layout.addWidget(export_button)
        main_layout.addLayout(axial_layout)
        main_layout.addLayout(sagittal_layout)
        
         
        self.position_bar = PositionBar(self)
        main_layout.addWidget(self.position_bar)

        for i in range(4):
            annotation_bar = AnnotationBar(i, self, self)
            annotation_layout.addWidget(annotation_bar)

        main_layout.addLayout(annotation_layout)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def load_dicom(self, file_path):
        try:
            dicom_data = pydicom.dcmread(file_path)
            if not hasattr(dicom_data, "pixel_array"):
                self.status_bar.showMessage("No pixel data found in the DICOM file.", 5000)
                return

            # Store the file path for use in export
            self.dicom_file_path = file_path
            
            # Load the pixel array and ensure it’s in a writable format
            self.dicom_data = dicom_data.pixel_array.copy()  # Copy to make it writable
            if self.dicom_data.ndim == 4:
                self.dicom_data = self.dicom_data[:, :, :, 0]

            # Prepare the static sagittal image
            width = self.dicom_data.shape[2]
            sagittal_image_data = np.rot90(self.dicom_data[:, :, width // 2], 1)
            
            # Convert to 8-bit grayscale and make a writable copy
            sagittal_image_data = np.ascontiguousarray((sagittal_image_data - np.min(sagittal_image_data)) / 
                                                    (np.max(sagittal_image_data) - np.min(sagittal_image_data)) * 255).astype(np.uint8)
            
            # Create QImage from the writable data
            q_image_sagittal = QImage(sagittal_image_data.data, sagittal_image_data.shape[1], sagittal_image_data.shape[0], QImage.Format_Grayscale8)
            
            # Set the QImage in the SagittalView
            self.sagittal_label.set_sagittal_image(q_image_sagittal)
            self.status_bar.showMessage("DICOM file loaded successfully.", 5000)

        except Exception as e:
            self.status_bar.showMessage(f"Failed to load DICOM file: {e}", 5000)
    
    def display_slice(self, slice_index):
        if self.dicom_data is None:
            return

        slice_index = max(0, min(slice_index, self.dicom_data.shape[0] - 1))
        self.current_slice = slice_index
        num_slices = self.dicom_data.shape[0] -1

        image = self.dicom_data[slice_index]
        image = np.ascontiguousarray((image - np.min(image)) / (np.max(image) - np.min(image)) * 255)
        image = image.astype(np.uint8)
        height, width = image.shape
        bytes_per_line = width
        q_image_axial = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        self.image_label.setPixmap(QPixmap.fromImage(q_image_axial))

        self.position_bar.set_position(self.current_slice / num_slices)
        self.frame_indicator.setText(f"{self.current_slice } / {num_slices}")
        self.sagittal_label.update()

    def display_slice_based_on_bar(self, bar_position):
        if self.dicom_data is None:
            return
        num_slices = self.dicom_data.shape[0]
        slice_index = int(bar_position * num_slices)
        self.display_slice(slice_index)

    def wheelEvent(self, event):
        if self.dicom_data is None:
            return

        num_slices = self.dicom_data.shape[0]
        if event.angleDelta().y() > 0:
            # Move forward; wrap to 0 if it exceeds num_slices - 1
            self.current_slice = (self.current_slice + 1) % num_slices
        else:
            # Move backward; wrap to num_slices - 1 if it goes below 0
            self.current_slice = (self.current_slice - 1) if self.current_slice > 0 else num_slices - 1

        self.display_slice(self.current_slice)
        
    def display_slice(self, slice_index):
        if self.dicom_data is None:
            return

        slice_index = max(0, min(slice_index, self.dicom_data.shape[0] - 1))
        self.current_slice = slice_index
        num_slices = self.dicom_data.shape[0] - 1

        image = self.dicom_data[slice_index]
        image = np.ascontiguousarray((image - np.min(image)) / (np.max(image) - np.min(image)) * 255)
        image = image.astype(np.uint8)
        height, width = image.shape
        bytes_per_line = width
        q_image_axial = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        self.image_label.setPixmap(QPixmap.fromImage(q_image_axial))

        self.position_bar.set_position(self.current_slice / num_slices)
        self.frame_indicator.setText(f"{self.current_slice} / {num_slices}")

        # Update annotation bars for the current frame
        for annotation_bar in self.annotation_bars:
            annotation_bar.update_annotations_for_frame(self.current_slice)

        self.sagittal_label.update()

    def export_annotations(self):
        if not self.dicom_file_path:
            self.status_bar.showMessage("Please load a DICOM file before exporting.", 5000)
            return

        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not directory:
            return

        dicom_filename = os.path.basename(self.dicom_file_path)
        json_filename = os.path.splitext(dicom_filename)[0] + ".json"
        json_path = os.path.join(directory, json_filename)

        annotation_data = {
            "annotations": {}
        }
        for bar in self.annotation_bars:
            for frame_index, annotations in bar.annotations_per_frame.items():
                if frame_index not in annotation_data["annotations"]:
                    annotation_data["annotations"][frame_index] = []
                for start_x, end_x, color in annotations:
                    annotation_data["annotations"][frame_index].append({
                        "label_index": bar.label_index,
                        "start_x": start_x,
                        "end_x": end_x,
                    })

        with open(json_path, 'w') as json_file:
            json.dump(annotation_data, json_file, indent=4)

        self.status_bar.showMessage(f"Annotations exported to {json_path}", 5000)
    
    