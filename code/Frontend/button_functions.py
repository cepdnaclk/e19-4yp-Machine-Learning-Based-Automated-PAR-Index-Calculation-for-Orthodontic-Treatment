import json
import base64
import tempfile
import numpy as np
import requests
import os
import trimesh
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from vtk.util.numpy_support import vtk_to_numpy
import vtk
import numpy
from stl import mesh
from commonHelper import RenderHelper

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

def load_stl(self):
    try:
        if self.fileType == "Upper Arch Segment":
            base64_stl_data = self.file_data['prep_file']
        elif self.fileType == "Lower Arch Segment":
            base64_stl_data = self.file_data['opposing_file']
        elif self.fileType == "Buccal Segment":
            base64_stl_data = self.file_data['buccal_file']
    except Exception as e:
        QMessageBox.warning(self, "Warning", "No file data to load. Register the patient!")
        return

    decoded_stl_data = base64.b64decode(base64_stl_data)

    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp_file:
            self.markers.clear()
            self.points.clear()
            temp_file.write(decoded_stl_data)
            temp_file_path = temp_file.name

            reader = vtk.vtkSTLReader()
            reader.SetFileName(temp_file_path)
            reader.Update()

            your_mesh = mesh.Mesh.from_file(temp_file_path)

            self.renderer.RemoveAllViewProps()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            self.renderer.AddActor(actor)
            self.renderer.ResetCamera()

            self.center = np.mean(vtk_to_numpy(reader.GetOutput().GetPoints().GetData()), axis=0)

            points = np.vstack(np.array([your_mesh.v0, your_mesh.v1, your_mesh.v2]))
            means = np.mean(points, axis=0)
            centered_points = points - means
            covariance_matrix = np.cov(centered_points, rowvar=False)
            eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

            sorted_indexes = np.argsort(eigenvalues)[::-1]
            principal_eigenvectors = eigenvectors[:, sorted_indexes]
            top_principal_eigenvectors = principal_eigenvectors[:, :3]
            eigenvectors = top_principal_eigenvectors
            eigenvalues = eigenvalues[sorted_indexes[:3]]

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
            self.text_actor.GetTextProperty().SetFontSize(20)
            self.text_actor.SetPosition(20, 30)
            self.renderer.AddActor(self.text_actor)

            self.update_disclaimer_text(self.fileType)

            self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
            style = CustomRenderHelper(self.renderer, self.center, self.vtkWidget.GetRenderWindow(), self.markers, self.points, self)
            self.interactor.SetInteractorStyle(style)
            self.interactor.Initialize()
            self.vtkWidget.GetRenderWindow().Render()

    except OSError as e:
        if e.errno == 28:
            QMessageBox.critical(self, "Error", "No space left on disk. Free up space on C: drive and try again.")
        else:
            QMessageBox.critical(self, "Error", f"Failed to load STL file: {str(e)}")
        print(f"OSError: {e}")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to load STL file: {str(e)}")
        print(f"Exception: {e}")
    finally:
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Failed to delete temp file {temp_file_path}: {e}")

def save_to_json(self):
    if not self.points:
        QMessageBox.warning(self, "Warning", "No Data To Save.")
        print("No points to save.")
        return

    json_data = {
        "measurement_type": self.measurement,
        "points": [{"point_name": point["name"], "coordinates": (point["x"], point["y"], point["z"])} for point in self.points]
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