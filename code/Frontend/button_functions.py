import json
import trimesh
import requests
import base64
import tempfile
import os
import vtk
import numpy as np
import gzip 
import io  
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from stl import mesh
from vtk.util.numpy_support import vtk_to_numpy
from commonHelper import RenderHelper
from patient_list import PatientListWindow 

from config import BASE_URL

def load_stl(self):
    """
    Fetches, decompresses, and directly renders the STL file without simplification.
    """
    if not self.current_patient or 'patient_id' not in self.current_patient:
        QMessageBox.warning(self, "Warning", "No patient selected. Please select a patient first.")
        return

    patient_id = self.current_patient['patient_id']
    endpoint_map = {"Upper Arch Segment": "prepFile", "Lower Arch Segment": "opposingFile", "Buccal Segment": "buccalFile"}
    file_key = endpoint_map.get(self.fileType)

    if not file_key:
        QMessageBox.critical(self, "Error", "Invalid file type selected.")
        return

    url = f"{BASE_URL}/api/patient/{patient_id}/{file_key}"
    print(f"Requesting STL file from: {url}")
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            base64_stl_data = response.json().get('fileData')
            if not base64_stl_data:
                QMessageBox.warning(self, "No File", f"No {self.fileType} file was found for this patient on the server.")
                return
        else:
            QMessageBox.critical(self, "API Error", f"Failed to fetch STL file. Status: {response.status_code}\nResponse: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(self, "Connection Error", f"Could not connect to the server to fetch the STL file.\n\nError: {e}")
        return

    temp_file_path = None
    try:
        self.update_score_display(None) # Clear previous scores

        gzipped_data = base64.b64decode(base64_stl_data)
        raw_stl_data = gzip.decompress(gzipped_data)

        # Save the raw STL data to a temporary file for VTK and numpy-stl
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp_file:
            temp_file.write(raw_stl_data)
            temp_file_path = temp_file.name

        self.markers.clear()
        self.points.clear()

        # Load the mesh using vtkSTLReader
        reader = vtk.vtkSTLReader()
        reader.SetFileName(temp_file_path)
        reader.Update()

        # Load the mesh using numpy-stl for PCA calculation
        your_mesh = mesh.Mesh.from_file(temp_file_path)

        # Standard rendering pipeline
        self.renderer.RemoveAllViewProps()
        self.renderer.AddViewProp(self.patient_name_annotation)
        self.renderer.AddViewProp(self.score_display_actor) # Re-add the score display
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
        self.stl_actor = actor # Store a reference to the STL model's actor
        self.renderer.ResetCamera()

        self.center = np.mean(vtk_to_numpy(reader.GetOutput().GetPoints().GetData()), axis=0)

        # Your PCA and axis-drawing logic
        points = np.vstack(np.array([your_mesh.v0, your_mesh.v1, your_mesh.v2]))
        means = np.mean(points, axis=0)
        centered_points = points - means
        covariance_matrix = np.cov(centered_points, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
        sorted_indexes = np.argsort(eigenvalues)[::-1]
        principal_eigenvectors = eigenvectors[:, sorted_indexes]
        top_principal_eigenvectors = principal_eigenvectors[:, :3]
        eigenvectors = top_principal_eigenvectors
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

        for i, vec in enumerate(eigenvectors.T):
            lineSource = vtk.vtkLineSource()
            lineSource.SetPoint1(self.center)
            lineSource.SetPoint2(self.center + vec * 10)
            lineMapper = vtk.vtkPolyDataMapper()
            lineMapper.SetInputConnection(lineSource.GetOutputPort())
            lineActor = vtk.vtkActor()
            lineActor.SetMapper(lineMapper)
            lineActor.GetProperty().SetColor(colors[i])
            lineActor.GetProperty().SetLineWidth(2)
            self.renderer.AddActor(lineActor)

        self.text_actor = vtk.vtkTextActor()
        self.text_actor.GetTextProperty().SetColor(0, 1, 0)
        self.text_actor.GetTextProperty().SetFontSize(14)
        self.text_actor.GetTextProperty().SetLineSpacing(1.2)
        self.text_actor.SetPosition(20, 10)
        self.renderer.AddActor(self.text_actor)

        self.update_disclaimer_text(self.fileType)

        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        # style = RenderHelper(self.renderer, self.center, self.vtkWidget.GetRenderWindow(), self.markers, self.points)
        # This is the new, correct way to call the unified RenderHelper
        style = RenderHelper(self.renderer, self.vtkWidget.GetRenderWindow(), self.markers, self.points, self)
        style.SetMotionFactor(8.0)  # Increase the motion factor
        self.interactor.SetInteractorStyle(style)
        self.interactor.Initialize()
        self.vtkWidget.GetRenderWindow().Render()
        print(f"Successfully rendered {self.fileType}.")

    except Exception as e:
        import traceback
        print("--- AN ERROR OCCURRED ---")
        traceback.print_exc()
        print("-------------------------")
        QMessageBox.critical(self, "Processing Error", f"The file was downloaded but could not be processed or rendered.\n\nError: {e}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def save_to_json(self):
    if not self.points:
        QMessageBox.warning(self, "Warning", "No Data To Save.")
        print("No points to save.")
        return

    # Sort the points alphabetically by 'name'
    sorted_points = sorted(
        self.points,
        key=lambda point: point["name"].lower()  # case-insensitive sorting
    )

    # Construct JSON data with sorted points
    json_data = {
        "measurement_type": self.measurement,
        "patient_name": self.current_patient.get('name'),
        "file_type": self.fileType,
        "points": [
            {
                "point_name": point["name"],
                "coordinates": (point["x"], point["y"], point["z"])
            }
            for point in sorted_points
        ]
    }

    file_path = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json)")[0]
    if file_path:
        with open(file_path, 'w') as outfile:
            json.dump(json_data, outfile, indent=4)
        print("Data saved to", file_path)

def undo_marker(self):
    if self.markers:
        last_marker = self.markers.pop()
        self.points.pop()
        if 'actor' in last_marker:
            self.renderer.RemoveActor(last_marker['actor'])
        if 'textActor' in last_marker:
            self.renderer.RemoveActor(last_marker['textActor'])
        self.vtkWidget.GetRenderWindow().Render()
        print("Last marker has been undone.")

def reset_markers(self):
    while self.markers:
        marker = self.markers.pop()
        self.points.pop()
        if 'actor' in marker:
            self.renderer.RemoveActor(marker['actor'])
        if 'textActor' in marker:
            self.renderer.RemoveActor(marker['textActor'])
    self.vtkWidget.GetRenderWindow().Render()
    print("All markers have been reset.")

def save_data(self):
    try:
        if not self.file_data or not hasattr(self, 'file_data') or 'patient_id' not in self.file_data:
            QMessageBox.warning(self, "Error", "No patient data available. Select a patient or register a patient first!")
            return

        # Send all points as new (excluding deleted ones)
        if self.points:
            url = f"{BASE_URL}/api/point/list"
            data = {
                "patient_id": self.file_data['patient_id'],
                "file_type": self.fileType,
                "measurement_type": self.measurement,
                "points": [{"point_name": p["name"], "coordinates": f"{p['x']},{p['y']},{p['z']}"} for p in self.points]
            }
            response = requests.post(url, json=data)
            if response.status_code != 201:
                QMessageBox.warning(self, "Error", f"Failed to save points: {response.text}")
                print(response.text, "\n", response)
                return

        QMessageBox.information(self, "Success", "Points saved successfully!")
        self.markers.clear()
        self.points.clear()
        self.renderer.RemoveAllViewProps()
        self.vtkWidget.GetRenderWindow().Render()

    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        print(f"Exception: {e}")

def load_points(self):
    try:
        if not self.file_data or not hasattr(self, 'file_data') or 'patient_id' not in self.file_data:
            QMessageBox.warning(self, "Warning", "No patient data available. Select a patient or register a patient first!")
            return

        if not hasattr(self, 'renderer') or self.renderer.GetActors().GetNumberOfItems() == 0:
            QMessageBox.warning(self, "Warning", "No STL file loaded. Load an STL file first!")
            return

        url = f'{BASE_URL}/api/point?patient_id={self.file_data["patient_id"]}'
        print(f"Requesting points from: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            points_data = response.json()
            print(f"Received points data: {points_data}")
            file_type_points = points_data.get(self.fileType, [])
            
            if not file_type_points:
                QMessageBox.information(self, "Info", f"No points found for {self.fileType}.")
                return

            self.markers.clear()
            self.points.clear()


            for point in file_type_points:
                coords = [float(x) for x in point['coordinates'].split(',')]
                position = (coords[0], coords[1], coords[2])
                label = point['pointName']

                sphereSource = vtk.vtkSphereSource()
                sphereSource.SetCenter(position)
                sphereSource.SetRadius(0.25)
                sphereSource.Update()

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(sphereSource.GetOutputPort())

                sphereActor = vtk.vtkActor()
                sphereActor.SetMapper(mapper)
                sphereActor.GetProperty().SetColor(1, 0, 0)

                textActor = vtk.vtkBillboardTextActor3D()
                textActor.SetInput(label)
                textProp = textActor.GetTextProperty()
                textProp.SetFontSize(18)
                textProp.SetColor(0, 1, 0)
                textProp.SetBold(True)
                textActor.SetPosition(position)

                self.renderer.AddActor(sphereActor)
                self.renderer.AddActor(textActor)

                self.markers.append({
                    "name": label,
                    "x": coords[0],
                    "y": coords[1],
                    "z": coords[2],
                    "actor": sphereActor,
                    "textActor": textActor,
                    "point_ID": point.get('pointId')  # Store for reference
                })

                self.points.append({
                    "name": label,
                    "x": coords[0],
                    "y": coords[1],
                    "z": coords[2],
                    "point_ID": point.get('pointId')  # Store for reference
                })

            self.vtkWidget.GetRenderWindow().Render()
            # QMessageBox.information(self, "Success", "Points loaded successfully!")
            popup = QLabel("Points loaded successfully!", self)
            popup.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip | Qt.WindowStaysOnTopHint)

            # Apply custom style with border-radius
            popup.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: #2a2a2a;
                    border: 2px solid #0D47A1;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 15px;
                    
                }
            """)
            # Center the popup in the middle of the main window
            popup.adjustSize()
            popup.move(self.geometry().center() - popup.rect().center())

            popup.show()
            QTimer.singleShot(1500, popup.close)
        else:
            QMessageBox.warning(self, "Error", f"Failed to load points: {response.text}")
            print(f"Error response: {response.text}, Status: {response.status_code}")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        print(f"Exception: {str(e)}")

def get_patient_list(self):
    """
    Fetches the list of patients from the API, displays them in a dialog,
    and connects the dialog's signal to the main window's slot.
    """
    try:
        # Fetch patient data from your Spring Boot backend
        url = f"{BASE_URL}/api/patient/patients"
        response = requests.get(url, timeout=5) # Added a timeout
        
        if response.status_code == 200:
            patients = response.json()
            if not patients:
                QMessageBox.information(self, "No Patients", "There are no registered patients in the database.")
                return

            # Create an instance of the patient list window
            # This window is now responsible for displaying the data
            self.patient_list_window = PatientListWindow(patients, self)
            
            # CRITICAL: Connect the signal from the dialog to the slot in MainWindow
            self.patient_list_window.patient_selected.connect(self.handle_patient_selection)
            
            # Show the dialog
            self.patient_list_window.exec_() # Use exec_ for a modal dialog

        else:
            QMessageBox.critical(self, "API Error", f"Failed to fetch patient list. Status: {response.status_code}\n{response.text}")

    except requests.exceptions.RequestException as e:
        QMessageBox.critical(self, "Connection Error", f"Could not connect to the server.\nPlease ensure the backend is running.\n\nError: {e}")

def calculate_par_score(self):
    """
    Tells the backend to calculate the PAR score for the current patient.
    """
    if not self.current_patient or 'patient_id' not in self.current_patient:
        QMessageBox.warning(self, "Warning", "No patient loaded. Please select a patient first.")
        return

    # 1. Clear everything from the 3D view
    self.renderer.RemoveAllViewProps()

    # 2. Re-add the persistent text elements we want to keep
    self.renderer.AddViewProp(self.patient_name_annotation)
    self.renderer.AddViewProp(self.score_display_actor)
    
    # 3. Clear the point data lists
    self.markers.clear()
    self.points.clear()

    patient_id = self.current_patient['patient_id']
    
    # The URL now includes the patient ID
    url = f"{BASE_URL}/api/par-score/calculate/{patient_id}"
    print(f"Requesting PAR score calculation from: {url}")

    try:
        # We make a POST request with NO body
        response = requests.post(url)

        if response.status_code == 200:
            response_data = response.json()
            # Call the new method in MainWindow to display the scores
            self.update_score_display(response_data)
        else:
            QMessageBox.critical(self, "API Error", f"Failed to calculate score. Status: {response.status_code}\n{response.text}")

    except requests.exceptions.RequestException as e:
        QMessageBox.critical(self, "Connection Error", f"Could not connect to the server.\n\nError: {e}")