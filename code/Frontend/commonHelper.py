# import vtk
# import numpy as np
# from PyQt5.QtWidgets import QInputDialog

# class RenderHelper(vtk.vtkInteractorStyleTrackballCamera):
#     def __init__(self, renderer, center, render_window, markers, points):
#         super(RenderHelper, self).__init__()
#         self.renderer = renderer
#         self.center = center
#         self.render_window = render_window
#         self.markers = markers
#         self.points = points
#         self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)

#     def leftButtonPressEvent(self, obj, event):
#         click_pos = self.GetInteractor().GetEventPosition()
#         picker = vtk.vtkCellPicker()
#         picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        
#         if picker.GetCellId() != -1:
#             pos = picker.GetPickPosition()
#             name, ok = QInputDialog.getText(None, "Point Name", "Enter point name:")
#             if ok and name:
#                 sphereSource = vtk.vtkSphereSource()
#                 sphereSource.SetCenter(pos)
#                 sphereSource.SetRadius(0.5)
#                 sphereSource.Update()

#                 mapper = vtk.vtkPolyDataMapper()
#                 mapper.SetInputConnection(sphereSource.GetOutputPort())

#                 sphereActor = vtk.vtkActor()
#                 sphereActor.SetMapper(mapper)
#                 sphereActor.GetProperty().SetColor(1, 0, 0)

#                 textActor = vtk.vtkBillboardTextActor3D()
#                 textActor.SetInput(name)
#                 textProp = textActor.GetTextProperty()
#                 textProp.SetFontSize(18)
#                 textProp.SetColor(0, 1, 0)
#                 textProp.SetBold(True)
#                 textActor.SetPosition(pos)

#                 self.renderer.AddActor(sphereActor)
#                 self.renderer.AddActor(textActor)

#                 self.markers.append({
#                     "name": name,
#                     "x": pos[0],
#                     "y": pos[1],
#                     "z": pos[2],
#                     "actor": sphereActor,
#                     "textActor": textActor
#                 })

#                 self.points.append({
#                     "name": name,
#                     "x": pos[0],
#                     "y": pos[1],
#                     "z": pos[2]
#                 })

#                 self.render_window.Render()
        
#         self.OnLeftButtonDown()


#     def add_marker(self, position):
#         # Create and place a sphere (marker)
#         sphereSource = vtk.vtkSphereSource()
#         sphereSource.SetCenter(position)
#         sphereSource.SetRadius(0.1)
#         sphereSource.Update()

#         mapper = vtk.vtkPolyDataMapper()
#         mapper.SetInputConnection(sphereSource.GetOutputPort())

#         sphereActor = vtk.vtkActor()
#         sphereActor.SetMapper(mapper)
#         sphereActor.GetProperty().SetColor(1, 0, 0)  # Red color for the marker

#         self.renderer.AddActor(sphereActor)

#         label, ok = QInputDialog.getText(None, "Input Marker Label", "Enter label for the marker:")
#         if ok and label:
#             # Create and display a label that moves with the marker
#             textActor = vtk.vtkBillboardTextActor3D()
#             textActor.SetInput(label)
#             textProp = textActor.GetTextProperty()
#             textProp.SetFontSize(18)
#             textProp.SetColor(0, 1, 0)
#             textProp.SetBold(True)
#             textActor.SetPosition(position)
#             self.renderer.AddActor(textActor)

#             self.renderWindow.Render()

#             # Save position, label, and actors to markers list
#             self.markers.append({
#                 "name": label,
#                 "x": position[0], 
#                 "y": position[1], 
#                 "z": position[2], 
#                 "actor": sphereActor, 
#                 "textActor": textActor
#             })

#             # Save position, label, and actors to point list
#             self.points.append({
#                 "name": label,
#                 "x": position[0], 
#                 "y": position[1], 
#                 "z": position[2]
#             })

#         else: 
#             self.renderer.RemoveActor(sphereActor)

#         self.input_active = False  # Reset flag after handling input
        
        


import vtk
from PyQt5.QtWidgets import QInputDialog, QMessageBox

class RenderHelper(vtk.vtkInteractorStyleTrackballCamera):
    """A unified interactor style to handle point placement, deletion, editing, and camera control."""
    def __init__(self, renderer, render_window, markers, points, main_window):
        super().__init__()
        self.renderer = renderer
        self.render_window = render_window
        self.markers = markers
        self.points = points
        self.main_window = main_window

        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent, -1.0)

    def leftButtonPressEvent(self, obj, event):
        click_pos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)

        if picker.GetCellId() != -1:
            picked_actor = picker.GetActor()
            
            marker_clicked = None
            marker_index = -1
            for i, marker in enumerate(self.markers):
                if marker.get("actor") == picked_actor:
                    marker_clicked = marker
                    marker_index = i
                    break

            if marker_clicked:
                # --- ACTION 1: HANDLE CLICK ON AN EXISTING MARKER ---
                self.show_marker_options(marker_clicked, marker_index)
            else:
                # --- ACTION 2: ADD A NEW MARKER ---
                self.add_new_marker(picker.GetPickPosition())
            # By simply returning here, we "consume" the event and do not
            # pass it to the default camera controls. This prevents the rotation.
            return
        
        # --- ACTION 3: ROTATE THE CAMERA ---
        self.OnLeftButtonDown()

    def show_marker_options(self, marker, index):
        """Creates and shows a message box with 'Edit' and 'Remove' options."""
        msgBox = QMessageBox(self.main_window)
        msgBox.setWindowTitle("Point Options")
        msgBox.setText(f"What would you like to do with point '{marker['name']}'?")
        msgBox.setIcon(QMessageBox.Question)

        # Add custom buttons
        editButton = msgBox.addButton("Edit Name", QMessageBox.ActionRole)
        removeButton = msgBox.addButton("Remove", QMessageBox.ActionRole)
        cancelButton = msgBox.addButton("Cancel", QMessageBox.RejectRole)
        
        msgBox.exec_() # Show the message box

        if msgBox.clickedButton() == editButton:
            self.edit_marker_name(marker, index)
        elif msgBox.clickedButton() == removeButton:
            self.delete_marker(marker, index)

    def edit_marker_name(self, marker, index):
        """Opens a dialog to edit the name of an existing point."""
        current_name = marker['name']
        new_name, ok = QInputDialog.getText(self.main_window, "Edit Point Name", "Enter new name:", text=current_name)
        
        if ok and new_name and new_name != current_name:
            # Update the name in the data lists
            self.markers[index]['name'] = new_name
            self.points[index]['name'] = new_name
            
            # Update the 3D text actor in the scene
            self.markers[index]['textActor'].SetInput(new_name)
            self.render_window.Render()
            print(f"Renamed point '{current_name}' to '{new_name}'")

    def delete_marker(self, marker, index):
        """Handles the logic for deleting a point."""
        self.renderer.RemoveActor(marker["actor"])
        self.renderer.RemoveActor(marker["textActor"])
        self.markers.pop(index)
        self.points.pop(index)
        self.render_window.Render()
        print(f"Removed point '{marker['name']}'")

    def add_new_marker(self, position):
        """Handles the logic for adding a new point."""
        # This method remains the same as before
        name, ok = QInputDialog.getText(self.main_window, "Point Name", "Enter point name:")
        if ok and name:
            sphereSource = vtk.vtkSphereSource()
            sphereSource.SetCenter(position)
            sphereSource.SetRadius(0.25)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphereSource.GetOutputPort())
            sphereActor = vtk.vtkActor()
            sphereActor.SetMapper(mapper)
            sphereActor.GetProperty().SetColor(1, 0, 0)
            self.renderer.AddActor(sphereActor)

            textActor = vtk.vtkBillboardTextActor3D()
            textActor.SetInput(name)
            textActor.GetTextProperty().SetFontSize(18)
            textActor.GetTextProperty().SetColor(0, 1, 0)
            textActor.GetTextProperty().SetBold(True)
            textActor.SetPosition(position)
            self.renderer.AddActor(textActor)

            self.markers.append({"name": name, "x": position[0], "y": position[1], "z": position[2], "actor": sphereActor, "textActor": textActor})
            self.points.append({"name": name, "x": position[0], "y": position[1], "z": position[2]})
            
            self.render_window.Render()