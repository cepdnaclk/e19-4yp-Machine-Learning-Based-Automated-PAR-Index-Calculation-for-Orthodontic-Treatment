# import sys
# import requests
# from PyQt5.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, 
#                              QPushButton, QComboBox, QLabel, QMessageBox)
# import vtk
# from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
# from button_functions import load_stl, save_to_json, undo_marker, reset_markers, save_data, load_points, get_patient_list, edit_selected_point
# from register_patient import RegisterWindow
# from disclaimers import (UPPER_ANTERIOR_SEGMENT, LOWER_ANTERIOR_SEGMENT, BUCCAL_SEGMENT)

# class MainWindow(QMainWindow):
#     def __init__(self, parent=None):
#         super(MainWindow, self).__init__(parent)
#         self.mainWidget = QWidget()
#         self.setCentralWidget(self.mainWidget)
#         self.mainLayout = QHBoxLayout()
#         self.mainWidget.setLayout(self.mainLayout)

#         self.setWindowTitle("PAR Index Calculation")
#         self.text_actor = vtk.vtkTextActor()
#         self.buttonPanel = QVBoxLayout()
#         self.mainLayout.addLayout(self.buttonPanel)
#         self.mainWidget.setStyleSheet("background-color: black;")

#         # It's good practice to declare these attributes even if they are empty initially
#         self.patient_list_window = None
#         self.current_patient = None
#         self.file_data = None

#         self.btn_register = QPushButton("Register Patient")
#         self.view_patients = QPushButton("View Patients")

#         self.btn_load = QPushButton("Load STL")

#         self.btn_load_points = QPushButton("Load Points")

#         self.label_filetype = QLabel('Select the file type:')
#         self.fileTypeComboBox = QComboBox()
#         self.fileTypeComboBox.addItems(
#             ["Upper Arch Segment", 
#              "Lower Arch Segment", 
#              "Buccal Segment"
#             ])
#         self.fileType = "Upper Arch Segment"  # Default value

#         self.fileTypeComboBox.currentIndexChanged.connect(self.update_file_type)

#         self.measurement = "undefined"
        
#         self.btn_save_json = QPushButton("Save to JSON")
#         self.btn_reset = QPushButton("Reset Markers")
#         self.btn_undo = QPushButton("Undo Marker")
#         self.btnSave = QPushButton("Save")

#         button_style = """
#         QPushButton, QComboBox, QLabel {
#             background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #0D47A1);
#             border: 2px solid #0D47A1;
#             border-radius: 20px;
#             padding: 10px;
#             margin: 5px;
#             font-size: 14px;
#             color: white;
#         }

#         QPushButton:hover, QComboBox:hover {
#             background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D47A1, stop:1 #2196F3);
#         }

#         QPushButton:pressed, QComboBox:pressed {
#             background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #0D47A1);
#         }

#         QComboBox {
#             color: white;
#             background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #0D47A1);
#         }

#         QComboBox::drop-down {
#             subcontrol-origin: padding;
#             subcontrol-position: top right;
#             width: 15px;
#             border-left-width: 1px;
#             border-left-color: darkgray;
#             border-left-style: solid;
#             border-top-right-radius: 10px;
#             border-bottom-right-radius: 10px;
#         }

#         QComboBox QAbstractItemView {
#             background-color: #ADD8E6; /* Light blue background */
#             color: black; /* Ensuring text is visible against light background */
#             selection-background-color: #5599FF; /* Different color for selection for better contrast */
#         }
#         """

#         uniform_width = 25
#         for btn in [self.btn_register,self.view_patients, self.label_filetype,self.fileTypeComboBox,self.btn_load, self.btn_load_points, self.btn_save_json, self.btn_reset, self.btn_undo, self.btnSave]:
#             if (btn == self.label_filetype):
#                 btn.setFixedHeight(uniform_width)
#                 btn.setStyleSheet("color: white; font-size: 14px; margin: 5px; border: 2px;")
#             else:
#                 btn.setStyleSheet(button_style)
#             self.buttonPanel.addWidget(btn)
#         # self.buttonPanel.addStretch()

#         self.buttonPanel.setContentsMargins(10, 0, 10, 0)

#         self.buttonPanel.addSpacing(2)
#         self.btn_register.clicked.connect(self.open_register_window)
#         self.view_patients.clicked.connect(lambda: get_patient_list(self))
#         self.btn_load.clicked.connect(lambda: load_stl(self))
#         self.btn_load_points.clicked.connect(lambda: load_points(self))
#         self.btn_save_json.clicked.connect(lambda: save_to_json(self))
#         self.btn_reset.clicked.connect(lambda: reset_markers(self))
#         self.btn_undo.clicked.connect(lambda: undo_marker(self))
#         self.btnSave.clicked.connect(lambda: save_data(self))

#         self.vtkWidget = QVTKRenderWindowInteractor(self.mainWidget)
#         self.mainLayout.addWidget(self.vtkWidget)
#         self.renderer = vtk.vtkRenderer()
#         self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
#         self.markers = []
#         self.points = []
#         self.selected_point = None

#     def update_disclaimer_text(self, new_text):
#         if hasattr(self, 'text_actor'):
#             disclaimer_text = {
#             "Upper Arch Segment": UPPER_ANTERIOR_SEGMENT,
#             "Lower Arch Segment": LOWER_ANTERIOR_SEGMENT,
#             "Buccal Segment": BUCCAL_SEGMENT,
#             }.get(new_text, "No disclaimer available for this type.")

#             self.text_actor.SetInput(disclaimer_text)
#             self.text_actor.GetTextProperty().SetFontSize(15) 
#             self.vtkWidget.GetRenderWindow().Render()  # Rerender to update the display
#         pass

#     def update_file_type(self, index):
#         # This method is called whenever the selected index in the combo box changes.
#         self.fileType = self.fileTypeComboBox.currentText()
#         self.update_disclaimer_text(self.fileType)
#         print("Selected File Type:", self.fileType)
    
#     def open_register_window(self):
#         # This function will be called when btn_register is clicked
#         self.register_window = RegisterWindow()  # Create an instance of RegisterWindow
#         self.register_window.data_ready.connect(self.handle_data_from_register)  # Connect the data_ready signal to handle_data_from_register
#         self.register_window.show()  # Show the RegisterWindow
    
#     # def handle_data_from_register(self, data):
#     #     self.file_data = data

#     def handle_data_from_register(self, data):
#         self.file_data = data
#         self.current_patient = data
#         if self.current_patient:
#             print("Current patient data updated:", self.current_patient.get('patient_id'))
#             print("File data updated:", self.current_patient.get('file_name', 'No file name provided'))
#         else:
#             print("No patient data received.")
#         print("File type:", self.fileType)

#     def handle_patient_selection(self, patient_summary_data):
#         """
#         **MODIFIED SLOT**
#         This is called when a patient is selected from the list.
#         It now fetches the FULL patient details using the patient's ID.
#         """
#         patient_id = patient_summary_data.get('patient_id')
#         if not patient_id:
#             QMessageBox.critical(self, "Error", "Selected patient has no ID.")
#             return

#         print(f"Fetching full details for patient ID: {patient_id}...")

#         try:
#             # **NEW**: API call to get the complete data for the selected patient
#             # Make sure this endpoint exists in your Spring Boot backend.
#             url = f"http://localhost:8080/api/patient/{patient_id}"
#             response = requests.get(url, timeout=10)

#             if response.status_code == 200:
#                 # This full_patient_data should contain the Base64 file strings
#                 full_patient_data = response.json()

#                 print(">>> KEYS FROM BACKEND API:", full_patient_data.keys())

#                 # Update the main window's state with the COMPLETE data
#                 self.current_patient = full_patient_data
#                 self.file_data = full_patient_data

#                 patient_name = self.current_patient.get('name', 'N/A')
#                 QMessageBox.information(self, "Patient Loaded", f"Patient '{patient_name}' has been loaded.\n\nYou can now select a file type and click 'Load STL'.")
#                 print(f"Successfully loaded full data for patient: {patient_name}")

#             else:
#                 # Handle cases where the patient details couldn't be fetched
#                 QMessageBox.critical(self, "API Error", f"Failed to fetch full patient details. Status: {response.status_code}\n{response.text}")
#                 self.current_patient = None
#                 self.file_data = None

#         except requests.exceptions.RequestException as e:
#             QMessageBox.critical(self, "Connection Error", f"Could not connect to the server to fetch patient details.\n\nError: {e}")
#             self.current_patient = None
#             self.file_data = None

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

import sys
import requests
from PyQt5.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QComboBox, QLabel, QMessageBox)
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# Make sure these files are in the same directory or your Python path
from button_functions import (load_stl, save_to_json, undo_marker, reset_markers, 
                              save_data, load_points, get_patient_list)
from register_patient import RegisterWindow
from disclaimers import (UPPER_ANTERIOR_SEGMENT, LOWER_ANTERIOR_SEGMENT, BUCCAL_SEGMENT)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("PAR Index Calculation")
        self.setGeometry(100, 100, 1200, 800) # Set a good default window size

        # --- Main Widget and Layout ---
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QHBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0) # Remove margins for a clean look
        self.mainWidget.setStyleSheet("background-color: black;")

        # --- Left Panel for Buttons ---
        # 1. Use a container widget for the left panel for a stable layout
        left_panel_container = QWidget()
        left_panel_container.setMaximumWidth(250) # Prevent the button panel from becoming too wide

        # 2. The vertical layout holds all the buttons
        self.buttonPanel = QVBoxLayout(left_panel_container)
        self.buttonPanel.setContentsMargins(10, 10, 10, 10)
        
        # --- Create all UI Widgets ---
        self.btn_register = QPushButton("Register Patient")
        self.view_patients = QPushButton("View Patients")
        self.label_filetype = QLabel('Select the file type:')
        self.fileTypeComboBox = QComboBox()
        self.fileTypeComboBox.addItems(["Upper Arch Segment", "Lower Arch Segment", "Buccal Segment"])
        self.btn_load = QPushButton("Load STL")
        self.btn_load_points = QPushButton("Load Points")
        self.btn_save_json = QPushButton("Save to JSON")
        self.btn_reset = QPushButton("Reset Markers")
        self.btn_undo = QPushButton("Undo Marker")
        self.btnSave = QPushButton("Save")
        
        # --- Define Styles ---
        button_style = """
            QPushButton, QComboBox {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #0D47A1);
                border: 2px solid #0D47A1;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding-top: 10px;
                padding-bottom: 5px;
                font-weight: bold;
            }
            QPushButton:hover, QComboBox:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D47A1, stop:1 #2196F3);
            }
            QComboBox QAbstractItemView {
                background-color: #ADD8E6;
                color: black;
                selection-background-color: #5599FF;
            }
        """
        
        left_panel_container.setStyleSheet(button_style)

        # Create a list of all widgets to be added to the panel
        widgets_to_add = [
            self.btn_register,
            self.view_patients,
            self.label_filetype,
            self.fileTypeComboBox,
            self.btn_load,
            self.btn_load_points,
            self.btn_save_json,
            self.btn_reset,
            self.btn_undo,
            self.btnSave
        ]

        # Add a stretch at the top for even spacing
        self.buttonPanel.addStretch(1)

        # Loop through the widgets and add them with a stretch in between
        for widget in widgets_to_add:
            self.buttonPanel.addWidget(widget)
            self.buttonPanel.addStretch(1)
        
        # --- VTK Render Window Panel ---
        self.vtkWidget = QVTKRenderWindowInteractor(self.mainWidget)

        # --- Assemble the Main Layout ---
        self.mainLayout.addWidget(left_panel_container)
        # Add the VTK widget with a stretch factor of 1 to make it expand
        self.mainLayout.addWidget(self.vtkWidget, 1) 

        # --- Initialize Class Attributes & VTK ---
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.1, 0.1) # Set a dark grey background
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

        # Create a corner annotation for the patient name
        self.patient_name_annotation = vtk.vtkCornerAnnotation()
        # Set text properties for bold and font size
        text_prop = self.patient_name_annotation.GetTextProperty()
        text_prop.SetBold(True)
        text_prop.SetFontSize(12)
        text_prop.SetColor(1, 1, 0) # Yellow color
        # Set the initial text
        self.update_patient_name_display(None) # Use the update method to set initial text
        
        # Add it to the renderer
        self.renderer.AddViewProp(self.patient_name_annotation)

        self.text_actor = vtk.vtkTextActor()
        self.markers = []
        self.points = []
        self.current_patient = None
        self.file_data = None
        self.patient_list_window = None
        self.register_window = None
        self.fileType = "Upper Arch Segment" # Default value
        self.measurement = "undefined"

        # --- Connect Signals to Slots ---
        self.btn_register.clicked.connect(self.open_register_window)
        self.view_patients.clicked.connect(lambda: get_patient_list(self))
        self.btn_load.clicked.connect(lambda: load_stl(self))
        self.btn_load_points.clicked.connect(lambda: load_points(self))
        self.btn_save_json.clicked.connect(lambda: save_to_json(self))
        self.btn_reset.clicked.connect(lambda: reset_markers(self))
        self.btn_undo.clicked.connect(lambda: undo_marker(self))
        self.btnSave.clicked.connect(lambda: save_data(self))
        self.fileTypeComboBox.currentIndexChanged.connect(self.update_file_type)

    def update_disclaimer_text(self, new_text):
        if hasattr(self, 'text_actor'):
            disclaimer_text = {
                "Upper Arch Segment": UPPER_ANTERIOR_SEGMENT,
                "Lower Arch Segment": LOWER_ANTERIOR_SEGMENT,
                "Buccal Segment": BUCCAL_SEGMENT,
            }.get(new_text, "")
            self.text_actor.SetInput(disclaimer_text)
            self.vtkWidget.GetRenderWindow().Render()

    def update_file_type(self, index):
        self.fileType = self.fileTypeComboBox.currentText()
        print(f"Selected File Type: {self.fileType}")
        self.update_disclaimer_text(self.fileType)
    
    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.data_ready.connect(self.handle_data_from_register)
        self.register_window.show()
    
    def handle_data_from_register(self, data):
        self.file_data = data
        self.current_patient = data
        # patient_name = self.current_patient.get('name', 'N/A')
        # QMessageBox.information(self, "Success", f"Patient '{patient_name}' registered. You can now load STL files.")
        self.update_patient_name_display(self.current_patient.get('name'))

    def handle_patient_selection(self, patient_summary_data):
        patient_id = patient_summary_data.get('patient_id')
        if not patient_id:
            QMessageBox.critical(self, "Error", "Selected patient has no ID.")
            return

        print(f"Fetching full details for patient ID: {patient_id}...")
        try:
            url = f"http://localhost:8080/api/patient/{patient_id}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                full_patient_data = response.json()
                self.current_patient = full_patient_data
                self.file_data = full_patient_data # For backward compatibility
                patient_name = self.current_patient.get('name', 'N/A')
                QMessageBox.information(self, "Patient Loaded", f"Patient '{patient_name}' has been loaded.")
                print(f"Successfully loaded full data for patient: {patient_name}")
                self.update_patient_name_display(patient_name)
            else:
                QMessageBox.critical(self, "API Error", f"Failed to fetch patient details. Status: {response.status_code}\n{response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to the server.\n\nError: {e}")


    def update_patient_name_display(self, name):
        """Updates the text in the top right corner with margins."""
        if name:
            # Add a newline for top margin and spaces for right margin
            display_text = f"\n Patient: {name}  " 
            self.patient_name_annotation.SetText(vtk.vtkCornerAnnotation.UpperRight, display_text)
        else:
            # Set default text with margins
            self.patient_name_annotation.SetText(vtk.vtkCornerAnnotation.UpperRight, "\n No Patient Loaded  ")
        
        # Re-render the window to show the change
        self.vtkWidget.GetRenderWindow().Render()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())