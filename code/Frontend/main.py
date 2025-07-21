import sys
import requests
from PyQt5.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QComboBox, QLabel, QMessageBox)
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# Make sure these files are in the same directory or your Python path
from button_functions import (load_stl, save_to_json, undo_marker, reset_markers, 
                              save_data, load_points, get_patient_list, calculate_par_score)
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
        self.btn_register = QPushButton("New Patient")
        self.view_patients = QPushButton("Select Patient")
        self.label_filetype = QLabel('Select the file type:')
        self.fileTypeComboBox = QComboBox()
        self.fileTypeComboBox.addItems(["Upper Arch Segment", "Lower Arch Segment", "Buccal Segment"])
        self.btn_load = QPushButton("Load STL")
        self.btn_load_points = QPushButton("Load Points")
        self.btn_save_json = QPushButton("Save to JSON")
        self.btn_reset = QPushButton("Reset Markers")
        self.btn_undo = QPushButton("Undo Marker")
        self.btnSave = QPushButton("Save")
        self.btn_calculate_par = QPushButton("Calculate PAR Score")
        
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
            self.btnSave,
            self.btn_calculate_par
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

        self.score_display_actor = vtk.vtkTextActor()
        score_prop = self.score_display_actor.GetTextProperty()
        score_prop.SetFontSize(16)
        score_prop.SetColor(1, 1, 0) # Yellow
        score_prop.SetBold(True)
        score_prop.SetLineSpacing(2)

        # Set the text alignment to centered
        # score_prop.SetJustificationToCentered()

        # Position the actor in the center of the window
        # Note: This is an initial position; it may not stay perfectly centered on resize
        window_width = self.geometry().width() - 250 # Subtract button panel width
        window_height = self.geometry().height()
        self.score_display_actor.SetPosition(window_width / 3, window_height / 1.5)
        
        self.renderer.AddViewProp(self.score_display_actor)

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
        self.btn_calculate_par.clicked.connect(lambda: calculate_par_score(self))
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
            self.patient_name_annotation.SetText(vtk.vtkCornerAnnotation.UpperRight, "\n Patient: N/A  ")
        
        # Re-render the window to show the change
        self.vtkWidget.GetRenderWindow().Render()

    def update_score_display(self, score_data):
        """Formats and displays the PAR score breakdown in the VTK window."""
        if score_data:
            # Build the multi-line string with the score details
            score_text = "PAR Score Breakdown:\n"
            score_text += f"  - Upper Anterior: {score_data.get('upperAnteriorScore', 'N/A')}\n"
            score_text += f"  - Lower Anterior: {score_data.get('lowerAnteriorScore', 'N/A')}\n"
            # Add other components here as you implement them
            score_text += "--------------------\n"
            score_text += f"  Final Score: {score_data.get('finalParScore', 'N/A')}"
            
            self.score_display_actor.SetInput(score_text)
        else:
            # If no data, clear the text
            self.score_display_actor.SetInput("")
        
        self.vtkWidget.GetRenderWindow().Render()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())