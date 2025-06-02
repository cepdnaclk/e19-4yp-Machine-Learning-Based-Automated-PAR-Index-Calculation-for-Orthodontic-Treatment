import base64
import trimesh
import gzip
import shutil
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QRadioButton,
                             QGroupBox,  QMessageBox, QMainWindow, QFileDialog)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
import requests
import os

class FileDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        
        # self.icon_label = QLabel()
        # self.icon_label.setFixedSize(50, 50)  # Set fixed size for the icon
        
        self.file_name_label = QLabel("No file selected")
        self.file_path = None

        #layout.addWidget(self.icon_label)
        layout.addWidget(self.file_name_label)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def set_file(self, file_path):
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_path)[1]
        if(file_extension != '.stl'):
            QMessageBox.critical(self, "Error", "Incorrect File Type")
        else:
            self.file_name_label.setText(file_name)
            self.file_path = file_path
            # Set the file icon (this assumes you have a file icon image in the working directory)
            #icon_pixmap = QPixmap('file_icon.png').scaled(self.icon_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            #self.icon_label.setPixmap(icon_pixmap)
            #self.titleLabel.setText(file_path)

class RegisterWindow(QMainWindow):

    data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Register Patient")
        self.setGeometry(100, 100, 800, 600)
        
        # Create the main widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.setCentralWidget(self.main_widget)
        
        self.patient_layout = QHBoxLayout()
        self.patient_input = QLineEdit()
        self.patient_input.setStyleSheet("padding: 10px; font-size: 16px; border-radius: 20px;")
        self.patient_input.setPlaceholderText("Patient name")
        self.patient_layout.addWidget(self.patient_input)
        
        self.treatment_type_group = QGroupBox("Treatment Type")
        self.treatment_type_layout = QHBoxLayout()
        self.pre_treatment_radio = QRadioButton('Pre Treatment')
        self.post_treatment_radio = QRadioButton('Post Treatment')
        self.treatment_type_layout.addWidget(self.pre_treatment_radio)
        self.treatment_type_layout.addWidget(self.post_treatment_radio) 
        self.treatment_type_group.setLayout(self.treatment_type_layout)
        
        files_layout = QHBoxLayout()
        # File Upload Groups
        opposing_group = QGroupBox('Lower Arch Segment')
        #buccal_group = QGroupBox('Buccal Segment')
        prep_group = QGroupBox('Upper Arch Segment')

        self.opposing_file_display = FileDisplayWidget()
        #self.buccal_file_display = FileDisplayWidget()
        self.prep_file_display = FileDisplayWidget()

        button_style = """
        QPushButton{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #0D47A1);
            border: 2px solid #0D47A1;
            border-radius: 20px;
            padding: 10px;
            margin: 5px;
            font-size: 14px;
            color: white;
        }

        QPushButton:hover{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D47A1, stop:1 #2196F3);
        }

        QPushButton:pressed{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #0D47A1);
        }
        """

        for group, display_widget in zip([opposing_group, prep_group],
                                         [self.opposing_file_display, self.prep_file_display]):
            button = QPushButton('Browse')
            button.setStyleSheet(button_style)
            button.clicked.connect(lambda _, b=button, d=display_widget: self.browse_file(b, d))

            layout = QVBoxLayout()
            layout.addWidget(display_widget)
            layout.addWidget(button)
            group.setLayout(layout)
            files_layout.addWidget(group)
        
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(button_style)     
        self.save_button.clicked.connect(self.register_patient)

        self.main_layout.addLayout(self.patient_layout)
        self.main_layout.addWidget(self.treatment_type_group)
        self.main_layout.addLayout(files_layout)
        self.main_layout.addWidget(self.save_button)
        self.main_widget.setLayout(self.main_layout)
        
    def gzip_compress_file(self, original_file):
        # Compress the file and create a temporary file
        compressed_file = original_file + '.gz'
        
        # Compress the file using gzip.
        with open(original_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_file
    
    def compress_file(original_file):
        compressed_file = original_file + '.gz'
        with open(original_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.writelines(f_in)
        return compressed_file

    def register_patient(self):
        """Register a patient and automatically merge STL files, saving buccal STL in the upper STL's directory."""
        # Collect data
        patient_data = {
            'name': self.patient_input.text(),
            'treatment_status': 'Pre' if self.pre_treatment_radio.isChecked() else 'Post'
        }

        files_data = {}
        temp_files = []  # Track temporary files

        # Validate inputs
        if not patient_data['name']:
            QMessageBox.warning(self, "Error", "Patient name is required.")
            return
        if not self.prep_file_display.file_path or not self.opposing_file_display.file_path:
            QMessageBox.warning(self, "Error", "Both upper and lower STL files are required.")
            return
        if not (self.pre_treatment_radio.isChecked() or self.post_treatment_radio.isChecked()):
            QMessageBox.warning(self, "Error", "Please select a treatment type.")
            return

        # Check file sizes
        max_size_mb = 100
        for path in [self.prep_file_display.file_path, self.opposing_file_display.file_path]:
            size_mb = os.path.getsize(path) / (1024 * 1024)
            if size_mb > max_size_mb:
                QMessageBox.critical(self, "Error", f"File {os.path.basename(path)} is too large ({size_mb:.2f} MB). Limit is {max_size_mb} MB.")
                return

        try:
            # Prepare upper and lower STL files
            prep_compressed = self.gzip_compress_file(self.prep_file_display.file_path)
            files_data['prep_file'] = (os.path.basename(prep_compressed),
                                    open(prep_compressed, 'rb'),
                                    'application/gzip')
            temp_files.append(prep_compressed)

            opposing_compressed = self.gzip_compress_file(self.opposing_file_display.file_path)
            files_data['opposing_file'] = (os.path.basename(opposing_compressed),
                                        open(opposing_compressed, 'rb'),
                                        'application/gzip')
            temp_files.append(opposing_compressed)

            # Merge upper and lower STL files
            buccal_base64 = None
            buccal_file_path = None
            try:
                # Load meshes
                upper_mesh = trimesh.load_mesh(self.prep_file_display.file_path)
                lower_mesh = trimesh.load_mesh(self.opposing_file_display.file_path)

                # Merge meshes
                combined_mesh = upper_mesh + lower_mesh

                # Save merged mesh to the same directory as upper STL
                upper_dir = os.path.dirname(self.prep_file_display.file_path)
                buccal_file_path = os.path.join(upper_dir, f"buccal_closed_{patient_data['name'].replace(' ', '_')}.stl")
                # Ensure unique filename
                base, ext = os.path.splitext(buccal_file_path)
                counter = 1
                while os.path.exists(buccal_file_path):
                    buccal_file_path = f"{base}_{counter}{ext}"
                    counter += 1
                combined_mesh.export(buccal_file_path)

                # Read buccal STL for base64 encoding
                with open(buccal_file_path, 'rb') as file:
                    buccal_base64 = base64.b64encode(file.read()).decode('utf-8')

                # Compress for backend
                compressed_buccal = self.gzip_compress_file(buccal_file_path)
                temp_files.append(compressed_buccal)
                files_data['buccal_file'] = (
                    'buccal_closed.stl.gz',
                    open(compressed_buccal, 'rb'),
                    'application/gzip')

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to merge STL files: {str(e)}")
                print(f"Error merging STL files: {e}")
                return

            # Send data to backend
            url = 'http://localhost:8080/api/patient/register'
            response = requests.post(url, data=patient_data, files=files_data)
            patient_id = response.json().get('patient_id')

            if response.status_code == 201:
                # Prepare data for emission
                data = {
                    'patient_id': patient_id,
                    'prep_file': base64.b64encode(open(self.prep_file_display.file_path, 'rb').read()).decode('utf-8'),
                    'opposing_file': base64.b64encode(open(self.opposing_file_display.file_path, 'rb').read()).decode('utf-8'),
                    'buccal_file': buccal_base64
                }

                self.data_ready.emit(data)
                QMessageBox.information(self, "Success", f"Patient registered successfully. Buccal STL saved as {buccal_file_path}")
                self.close()
            else:
                QMessageBox.critical(self, "Error", f"Failed to register patient: {response.text}")
                print(f"Error: {response.text}, Status: {response.status_code}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            print(f"Exception: {e}")
        finally:
            # Clean up files
            for _, file_tuple in files_data.items():
                file_tuple[1].close()
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        print(f"Failed to delete temp file {temp_file}: {e}")

    def browse_file(self, button, display_widget):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "STL Files (*.stl)")
        if file_path:
            display_widget.set_file(file_path)