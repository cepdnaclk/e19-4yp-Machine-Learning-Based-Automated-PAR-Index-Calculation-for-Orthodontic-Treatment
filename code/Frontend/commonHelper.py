import vtk
import numpy as np
from PyQt5.QtWidgets import QInputDialog

class RenderHelper(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, renderer, center, render_window, markers, points):
        super(RenderHelper, self).__init__()
        self.renderer = renderer
        self.center = center
        self.render_window = render_window
        self.markers = markers
        self.points = points
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)

    def leftButtonPressEvent(self, obj, event):
        click_pos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        
        if picker.GetCellId() != -1:
            pos = picker.GetPickPosition()
            name, ok = QInputDialog.getText(None, "Point Name", "Enter point name:")
            if ok and name:
                sphereSource = vtk.vtkSphereSource()
                sphereSource.SetCenter(pos)
                sphereSource.SetRadius(0.5)
                sphereSource.Update()

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(sphereSource.GetOutputPort())

                sphereActor = vtk.vtkActor()
                sphereActor.SetMapper(mapper)
                sphereActor.GetProperty().SetColor(1, 0, 0)

                textActor = vtk.vtkBillboardTextActor3D()
                textActor.SetInput(name)
                textProp = textActor.GetTextProperty()
                textProp.SetFontSize(18)
                textProp.SetColor(0, 1, 0)
                textProp.SetBold(True)
                textActor.SetPosition(pos)

                self.renderer.AddActor(sphereActor)
                self.renderer.AddActor(textActor)

                self.markers.append({
                    "name": name,
                    "x": pos[0],
                    "y": pos[1],
                    "z": pos[2],
                    "actor": sphereActor,
                    "textActor": textActor
                })

                self.points.append({
                    "name": name,
                    "x": pos[0],
                    "y": pos[1],
                    "z": pos[2]
                })

                self.render_window.Render()
        
        self.OnLeftButtonDown()


    def add_marker(self, position):
        # Create and place a sphere (marker)
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(position)
        sphereSource.SetRadius(0.1)
        sphereSource.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphereSource.GetOutputPort())

        sphereActor = vtk.vtkActor()
        sphereActor.SetMapper(mapper)
        sphereActor.GetProperty().SetColor(1, 0, 0)  # Red color for the marker

        self.renderer.AddActor(sphereActor)

        label, ok = QInputDialog.getText(None, "Input Marker Label", "Enter label for the marker:")
        if ok and label:
            # Create and display a label that moves with the marker
            textActor = vtk.vtkBillboardTextActor3D()
            textActor.SetInput(label)
            textProp = textActor.GetTextProperty()
            textProp.SetFontSize(18)
            textProp.SetColor(0, 1, 0)
            textProp.SetBold(True)
            textActor.SetPosition(position)
            self.renderer.AddActor(textActor)

            self.renderWindow.Render()

            # Save position, label, and actors to markers list
            self.markers.append({
                "name": label,
                "x": position[0], 
                "y": position[1], 
                "z": position[2], 
                "actor": sphereActor, 
                "textActor": textActor
            })

            # Save position, label, and actors to point list
            self.points.append({
                "name": label,
                "x": position[0], 
                "y": position[1], 
                "z": position[2]
            })

        else: 
            self.renderer.RemoveActor(sphereActor)

        self.input_active = False  # Reset flag after handling input
        
        

