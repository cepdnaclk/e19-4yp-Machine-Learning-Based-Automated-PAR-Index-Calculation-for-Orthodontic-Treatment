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
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from stl import mesh
from vtk.util.numpy_support import vtk_to_numpy
from commonHelper import RenderHelper
from patient_list import PatientListWindow 


# def load_stl(self):
#     """
#     Fetches, decompresses, robustly loads, simplifies, and then renders the STL file.
#     """
#     if not self.current_patient or 'patient_id' not in self.current_patient:
#         QMessageBox.warning(self, "Warning", "No patient selected. Please select a patient from the 'View Patients' list first.")
#         return

#     patient_id = self.current_patient['patient_id']
#     endpoint_map = {"Upper Arch Segment": "prepFile", "Lower Arch Segment": "opposingFile", "Buccal Segment": "buccalFile"}
#     file_key = endpoint_map.get(self.fileType)

#     if not file_key:
#         QMessageBox.critical(self, "Error", "Invalid file type selected.")
#         return

#     url = f"http://localhost:8080/api/patient/{patient_id}/{file_key}"
#     print(f"Requesting STL file from: {url}")

#     try:
#         response = requests.get(url, timeout=60)
#         if response.status_code == 200:
#             base64_stl_data = response.json().get('fileData')
#             if not base64_stl_data:
#                 QMessageBox.warning(self, "No File", f"No {self.fileType} file was found for this patient on the server.")
#                 return
#         else:
#             QMessageBox.critical(self, "API Error", f"Failed to fetch STL file. Status: {response.status_code}\nResponse: {response.text}")
#             return
#     except requests.exceptions.RequestException as e:
#         QMessageBox.critical(self, "Connection Error", f"Could not connect to the server to fetch the STL file.\n\nError: {e}")
#         return

#     simplified_temp_path = None
#     try:
#         gzipped_data = base64.b64decode(base64_stl_data)
#         raw_stl_data = gzip.decompress(gzipped_data)
#         stl_file_in_memory = io.BytesIO(raw_stl_data)

#         print("Loading mesh from memory for simplification...")
#         loaded_object = trimesh.load(stl_file_in_memory, file_type='stl')
        
#         # --- THIS IS THE CRITICAL FIX FOR YOUR BUCCAL FILE ---
#         # Ensure we have a single Trimesh object to work with
#         if isinstance(loaded_object, trimesh.Scene):
#             print("Loaded a Scene object; converting to a single mesh.")
#             mesh_to_simplify = loaded_object.dump(concatenate=True)
#         elif isinstance(loaded_object, trimesh.Trimesh):
#             mesh_to_simplify = loaded_object
#         else:
#             raise TypeError(f"Trimesh loaded an unexpected object type: {type(loaded_object)}")
#         # --- END OF FIX ---

#         # Simplification logic now runs on a guaranteed Trimesh object
#         target_face_count = 500000
#         print(f"Original face count: {len(mesh_to_simplify.faces)}. Simplifying to ~{target_face_count} faces...")
#         if len(mesh_to_simplify.faces) > target_face_count:
#             simplified_mesh = mesh_to_simplify.simplify_quadratic_decimation(target_face_count)
#         else:
#             simplified_mesh = mesh_to_simplify

#         with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as simplified_temp_file:
#             simplified_mesh.export(simplified_temp_file.name)
#             simplified_temp_path = simplified_temp_file.name

#         # --- The rest of your rendering logic ---
#         self.markers.clear()
#         self.points.clear()

#         reader = vtk.vtkSTLReader()
#         reader.SetFileName(simplified_temp_path)
#         reader.Update()

#         your_mesh = mesh.Mesh.from_file(simplified_temp_path)

#         self.renderer.RemoveAllViewProps()
#         mapper = vtk.vtkPolyDataMapper()
#         mapper.SetInputConnection(reader.GetOutputPort())

#         actor = vtk.vtkActor()
#         actor.SetMapper(mapper)
#         self.renderer.AddActor(actor)
#         self.renderer.ResetCamera()

#         self.center = np.mean(vtk_to_numpy(reader.GetOutput().GetPoints().GetData()), axis=0)

#         # (Your PCA and axis-drawing logic)
#         points = np.vstack(np.array([your_mesh.v0, your_mesh.v1, your_mesh.v2]))
#         means = np.mean(points, axis=0)
#         centered_points = points - means
#         covariance_matrix = np.cov(centered_points, rowvar=False)
#         eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
#         sorted_indexes = np.argsort(eigenvalues)[::-1]
#         principal_eigenvectors = eigenvectors[:, sorted_indexes]
#         top_principal_eigenvectors = principal_eigenvectors[:, :3]
#         eigenvectors = top_principal_eigenvectors
#         colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

#         for i, vec in enumerate(eigenvectors.T):
#             lineSource = vtk.vtkLineSource()
#             lineSource.SetPoint1(self.center)
#             lineSource.SetPoint2(self.center + vec * 10)
#             lineMapper = vtk.vtkPolyDataMapper()
#             lineMapper.SetInputConnection(lineSource.GetOutputPort())
#             lineActor = vtk.vtkActor()
#             lineActor.SetMapper(lineMapper)
#             lineActor.GetProperty().SetColor(colors[i])
#             lineActor.GetProperty().SetLineWidth(2)
#             self.renderer.AddActor(lineActor)

#         self.text_actor = vtk.vtkTextActor()
#         self.text_actor.GetTextProperty().SetColor(0, 1, 0)
#         self.text_actor.GetTextProperty().SetFontSize(20)
#         self.text_actor.SetPosition(20, 30)
#         self.renderer.AddActor(self.text_actor)

#         self.update_disclaimer_text(self.fileType)

#         self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
#         style = RenderHelper(self.renderer, self.center, self.vtkWidget.GetRenderWindow(), self.markers, self.points)
#         style.SetMotionFactor(2.0)
#         self.interactor.SetInteractorStyle(style)
#         self.interactor.Initialize()
#         self.vtkWidget.GetRenderWindow().Render()
#         print(f"Successfully rendered simplified {self.fileType}.")

#     except Exception as e:
#         import traceback
#         print("--- AN ERROR OCCURRED ---")
#         traceback.print_exc()
#         print("-------------------------")
#         QMessageBox.critical(self, "Processing Error", f"The file was downloaded but could not be processed or rendered.\n\nError: {e}")
#     finally:
#         if simplified_temp_path and os.path.exists(simplified_temp_path):
#             os.remove(simplified_temp_path)

# TEMPORARY version of load_stl to save the file for testing

def load_stl(self):
    """
    Fetches, decompresses, and directly renders the STL file without simplification.
    """
    if not self.current_patient or 'patient_id' not in self.current_patient:
        QMessageBox.warning(self, "Warning", "No patient selected. Please select a patient from the 'View Patients' list first.")
        return

    patient_id = self.current_patient['patient_id']
    endpoint_map = {"Upper Arch Segment": "prepFile", "Lower Arch Segment": "opposingFile", "Buccal Segment": "buccalFile"}
    file_key = endpoint_map.get(self.fileType)

    if not file_key:
        QMessageBox.critical(self, "Error", "Invalid file type selected.")
        return

    url = f"http://localhost:8080/api/patient/{patient_id}/{file_key}"
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
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
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
        style = RenderHelper(self.renderer, self.center, self.vtkWidget.GetRenderWindow(), self.markers, self.points)
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

class CustomRenderHelper(RenderHelper):
    def __init__(self, renderer, center, render_window, markers, points, main_window):
        super().__init__(renderer, center, render_window, markers, points)
        self.main_window = main_window

    def leftButtonPressEvent(self, obj, event):
        click_pos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        actor = picker.GetActor()
        print(f"Clicked at {click_pos}, picked actor: {actor}")
        if actor:
            for i, marker in enumerate(self.markers):
                if marker.get("actor") == actor:
                    # Show confirmation dialog
                    reply = QMessageBox.question(
                        self.main_window,
                        "Confirm Removal",
                        f"Do you want to remove the point '{marker['name']}'?",
                        QMessageBox.Ok | QMessageBox.Cancel,
                        QMessageBox.Cancel
                    )
                    if reply == QMessageBox.Ok:
                        # Remove point
                        self.renderer.RemoveActor(marker["actor"])
                        self.renderer.RemoveActor(marker["textActor"])
                        self.markers.pop(i)
                        self.points.pop(i)
                        self.render_window.Render()
                        print(f"Removed point: {self.points[i] if i < len(self.points) else 'last'}")
                    else:
                        print(f"Point '{marker['name']}' removal canceled")
                    return
        # Allow new point placement for non-point clicks
        super().leftButtonPressEvent(obj, event)



# def save_to_json(self):
#     if not self.points:
#         QMessageBox.warning(self, "Warning", "No Data To Save.")
#         print("No points to save.")
#         return

#     json_data = {
#         "measurement_type": self.measurement,
#         "points": [{"point_name": point["name"], "coordinates": (point["x"], point["y"], point["z"])} for point in self.points]
#     }
#     file_path = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json)")[0]
#     if file_path:
#         with open(file_path, 'w') as outfile:
#             json.dump(json_data, outfile, indent=4)
#         print("Data saved to", file_path)

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
        if not hasattr(self, 'file_data') or 'patient_id' not in self.file_data:
            QMessageBox.warning(self, "Error", "No patient data available. Register a patient first!")
            return

        # Send all points as new (excluding deleted ones)
        if self.points:
            url = 'http://localhost:8080/api/point/list'
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
        if not hasattr(self, 'file_data') or 'patient_id' not in self.file_data:
            QMessageBox.warning(self, "Warning", "No patient data available. Register a patient first!")
            return

        if not hasattr(self, 'renderer') or self.renderer.GetActors().GetNumberOfItems() == 0:
            QMessageBox.warning(self, "Warning", "No STL file loaded. Load an STL file first!")
            return

        url = f'http://localhost:8080/api/point?patient_id={self.file_data["patient_id"]}'
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
                sphereSource.SetRadius(0.3)
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
            QMessageBox.information(self, "Success", "Points loaded successfully!")
        else:
            QMessageBox.warning(self, "Error", f"Failed to load points: {response.text}")
            print(f"Error response: {response.text}, Status: {response.status_code}")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        print(f"Exception: {str(e)}")

def edit_selected_point(self):
    if not hasattr(self, 'selected_point') or not self.selected_point:
        QMessageBox.warning(self, "Warning", "No point selected. Click a point to select it.")
        return

    dialog = PointEditDialog(self.selected_point, self)
    if dialog.exec_():
        updated_point = dialog.get_updated_point()
        if updated_point:
            # Update point in memory
            for i, point in enumerate(self.points):
                if point == self.selected_point:
                    self.points[i].update(updated_point)
                    # Update marker display
                    marker = self.markers[i]
                    marker["name"] = updated_point["name"]
                    marker["x"] = updated_point["x"]
                    marker["y"] = updated_point["y"]
                    marker["z"] = updated_point["z"]
                    # Update sphere position
                    sphere_source = vtk.vtkSphereSource()
                    sphere_source.SetCenter(updated_point["x"], updated_point["y"], updated_point["z"])
                    sphere_source.SetRadius(0.3)
                    sphere_source.Update()
                    mapper = vtk.vtkPolyDataMapper()
                    mapper.SetInputConnection(sphere_source.GetOutputPort())
                    marker["actor"].SetMapper(mapper)
                    # Update text label
                    marker["textActor"].SetInput(updated_point["name"])
                    marker["textActor"].SetPosition(updated_point["x"], updated_point["y"], updated_point["z"])
                    break
            self.vtkWidget.GetRenderWindow().Render()
            self.selected_point = None  # Clear selection
            QMessageBox.information(self, "Success", "Point updated locally. Press Save to update in database.")


def get_patient_list(self):
    """
    Fetches the list of patients from the API, displays them in a dialog,
    and connects the dialog's signal to the main window's slot.
    """
    try:
        # Fetch patient data from your Spring Boot backend
        url = 'http://localhost:8080/api/patient/patients'
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
