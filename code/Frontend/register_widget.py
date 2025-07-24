# register_widget.py

# Trying to create a self-contained embeddable widget for patient registration
# Which will embed into the right side of main application window

import base64
import gzip
import shutil
import os
import requests
import trimesh
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
                             QLabel, QRadioButton, QGroupBox, QMessageBox, QFileDialog)
from PyQt5.QtCore import pyqtSignal

from config import BASE_URL

class FileDisplayWidget(QWidget):
    """A helper widget to show the selected file name."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.file_name_label = QLabel("No file selected")
        self.file_path = None
        layout.addWidget(self.file_name_label)
        layout.addStretch()
    
    def set_file(self, file_path):
        if file_path and os.path.splitext(file_path)[1].lower() == '.stl':
            self.file_name_label.setText(os.path.basename(file_path))
            self.file_path = file_path
        else:
            self.file_name_label.setText("No file selected")
            self.file_path = None
            if file_path: # Only show error if a file was actually selected
                QMessageBox.critical(self, "Error", "Incorrect File Type. Please select a .stl file.")


class RegisterPatientWidget(QWidget):
    """An embeddable widget for patient registration."""
    # Signal to notify MainWindow that registration is done and to pass the data
    registration_finished = pyqtSignal(dict) 

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- UI Setup (same as your RegisterWindow) ---
        main_layout = QVBoxLayout(self) # Set the layout directly on the QWidget

        patient_layout = QHBoxLayout()
        self.patient_input = QLineEdit()
        self.patient_input.setPlaceholderText("Patient name")
        patient_layout.addWidget(self.patient_input)
        
        self.treatment_type_group = QGroupBox("Treatment Type")
        treatment_type_layout = QHBoxLayout(self.treatment_type_group)
        self.pre_treatment_radio = QRadioButton('Pre Treatment')
        self.post_treatment_radio = QRadioButton('Post Treatment')
        treatment_type_layout.addWidget(self.pre_treatment_radio)
        treatment_type_layout.addWidget(self.post_treatment_radio)
        
        files_layout = QHBoxLayout()
        opposing_group = QGroupBox('Lower Arch Segment')
        prep_group = QGroupBox('Upper Arch Segment')
        self.opposing_file_display = FileDisplayWidget()
        self.prep_file_display = FileDisplayWidget()

        for group, display_widget in zip([opposing_group, prep_group], [self.opposing_file_display, self.prep_file_display]):
            button = QPushButton('Browse')
            button.clicked.connect(lambda _, d=display_widget: self.browse_file(d))
            layout = QVBoxLayout(group)
            layout.addWidget(display_widget)
            layout.addWidget(button)
            files_layout.addWidget(group)
        
        self.save_button = QPushButton("Register and Save")
        self.save_button.clicked.connect(self.register_patient)

        main_layout.addLayout(patient_layout)
        main_layout.addWidget(self.treatment_type_group)
        main_layout.addLayout(files_layout)
        main_layout.addWidget(self.save_button)
        main_layout.addStretch(1) # Pushes widgets to the top

    def browse_file(self, display_widget):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "STL Files (*.stl)")
        if file_path:
            display_widget.set_file(file_path)

    def gzip_compress_file(self, original_file):
        compressed_file = original_file + '.gz'
        with open(original_file, 'rb') as f_in, gzip.open(compressed_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        return compressed_file

    def register_patient(self):
        # --- This logic is the same, but it emits a different signal at the end ---
        # 1. Validation
        if not self.patient_input.text():
            QMessageBox.warning(self, "Error", "Patient name is required.")
            return
        if not self.prep_file_display.file_path or not self.opposing_file_display.file_path:
            QMessageBox.warning(self, "Error", "Both upper and lower STL files are required.")
            return
        if not (self.pre_treatment_radio.isChecked() or self.post_treatment_radio.isChecked()):
            QMessageBox.warning(self, "Error", "Please select a treatment type.")
            return
        
        # 2. Prepare data for backend API
        patient_data = {
            'name': self.patient_input.text(),
            'treatment_status': 'Pre' if self.pre_treatment_radio.isChecked() else 'Post'
        }
        
        files_to_upload = {}
        temp_files_to_clean = []
        try:
            # Prepare files for multipart upload
            prep_compressed = self.gzip_compress_file(self.prep_file_display.file_path)
            temp_files_to_clean.append(prep_compressed)
            files_to_upload['prep_file'] = (os.path.basename(prep_compressed), open(prep_compressed, 'rb'), 'application/gzip')

            opposing_compressed = self.gzip_compress_file(self.opposing_file_display.file_path)
            temp_files_to_clean.append(opposing_compressed)
            files_to_upload['opposing_file'] = (os.path.basename(opposing_compressed), open(opposing_compressed, 'rb'), 'application/gzip')
            
            # (Your logic for creating the buccal file would go here as well)

            # 3. Send data to backend
            url = f'{BASE_URL}/api/patient/register'
            response = requests.post(url, data=patient_data, files=files_to_upload)
            
            # Close file handles before cleaning up
            for _, file_tuple in files_to_upload.items():
                file_tuple[1].close()

            if response.status_code == 201:
                # 4. On success, prepare data for the 3D view
                patient_id = response.json().get('patient_id')
                
                # We need to re-read the original (uncompressed) files to get their Base64 data
                with open(self.prep_file_display.file_path, 'rb') as f:
                    prep_base64 = base64.b64encode(f.read()).decode('utf-8')
                with open(self.opposing_file_display.file_path, 'rb') as f:
                    opposing_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                # Your logic to get buccal_base64
                buccal_base64 = "" # Placeholder

                data_for_3d_view = {
                    'patient_id': patient_id,
                    'name': patient_data['name'],
                    'prepFile': prep_base64,       # Use camelCase to match what the backend sends
                    'opposingFile': opposing_base64, # for consistency
                    'buccalFile': buccal_base64
                }

                QMessageBox.information(self, "Success", "Patient registered successfully!")
                self.registration_finished.emit(data_for_3d_view) # Emit signal to MainWindow
            else:
                QMessageBox.critical(self, "Error", f"Failed to register patient: {response.text}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            # Cleanup temporary compressed files
            for temp_file in temp_files_to_clean:
                if os.path.exists(temp_file):
                    os.remove(temp_file)