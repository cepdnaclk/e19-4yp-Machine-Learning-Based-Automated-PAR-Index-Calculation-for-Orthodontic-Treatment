# # Add this code to the patient_list.py file, around line 10
# import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QComboBox, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView
# from PyQt5.QtGui import QColor
# from PyQt5.QtCore import Qt

# class PatientListWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Patient List")
#         self.setGeometry(100, 100, 800, 600)

#         button_style = """
#         QPushButton{
#             background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #0D47A1);
#             border: 2px solid #0D47A1;
#             border-radius: 20px;
#             padding: 10px;
#             margin: 5px;
#             font-size: 14px;
#             color: white;
#         }

#         QPushButton:hover{
#             background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D47A1, stop:1 #2196F3);
#         }

#         QPushButton:pressed{
#             background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #0D47A1);
#         }
#         """

#         # Main widget and layout
#         self.main_widget = QWidget()
#         self.main_layout = QVBoxLayout()
#         self.setCentralWidget(self.main_widget)
        
#         # Patient table setup
#         self.patient_table = QTableWidget()
#         self.patient_table.setRowCount(0)
#         self.patient_table.setColumnCount(4)
#         self.patient_table.setHorizontalHeaderLabels(["id","Patient Name","Pre_PAR_Score","Post_PAR_Score"])
#         self.patient_table.verticalHeader().setVisible(False)  # Hide row numbers
#         self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
#         # Set selection behavior and mode
#         self.patient_table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.patient_table.setSelectionMode(QTableWidget.SingleSelection)


#         # Add a separator between the header and data rows
#         self.patient_table.setStyleSheet("""
# QTableWidget {
#     background-color: white;
#     gridline-color: #e0e0e0;
# }
# QTableWidget::item {
#     border-bottom: 1px solid #e0e0e0;
#     color: black;
# }
# QTableWidget::item:selected {
#     background-color: #1770cb;
#     color: white;
# }
# QHeaderView::section {
#     background-color: #f0f0f0;
#     border: 1px solid #d0d0d0;
#     padding: 4px;
# }
# """)

#         # Connect the cell selection to a function to select the entire row
#         self.patient_table.itemSelectionChanged.connect(self.select_entire_row)

#         # Add the patient table to the main layout
#         self.main_layout.addWidget(self.patient_table)
#         self.main_widget.setLayout(self.main_layout)
        
#         # View Points Button
#         self.btn_view_points = QPushButton("Select Patient")
#         self.btn_view_points.setStyleSheet(button_style)
#         self.main_layout.addWidget(self.btn_view_points)

#     def select_entire_row(self):
#         selected_items = self.patient_table.selectedItems()
#         if selected_items:
#             row = selected_items[0].row()
            
#             # Block signals temporarily to avoid recursion
#             self.patient_table.blockSignals(True)
#             self.patient_table.selectRow(row)
#             self.patient_table.blockSignals(False)
            
#             # Print the row data once
#             row_texts = [self.patient_table.item(row, col).text() for col in range(self.patient_table.columnCount())]

# patient_list.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import pyqtSignal

class PatientListWindow(QDialog):
    """
    A dialog window to display a list of patients and allow selection.
    Emits a signal with the selected patient's data.
    """
    # Define a signal that will carry a dictionary (the patient data)
    patient_selected = pyqtSignal(dict)

    def __init__(self, patients_data, parent=None):
        super().__init__(parent)
        self.patients_data = patients_data  # Store the raw patient data
        self.setWindowTitle("Select a Patient")
        self.setMinimumSize(600, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Table to display patients
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(4)
        self.patient_table.setHorizontalHeaderLabels(["Patient ID", "Name", "Pre-PAR Score", "Post-PAR Score"])
        self.patient_table.setRowCount(len(self.patients_data))
        self.patient_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.patient_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.patient_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Make table read-only
        
        # Populate the table
        for i, patient in enumerate(self.patients_data):
            self.patient_table.setItem(i, 0, QTableWidgetItem(str(patient.get("patient_id", "N/A"))))
            self.patient_table.setItem(i, 1, QTableWidgetItem(patient.get("name", "N/A")))
            self.patient_table.setItem(i, 2, QTableWidgetItem(str(patient.get("pre_PAR_score", "N/A"))))
            self.patient_table.setItem(i, 3, QTableWidgetItem(str(patient.get("post_PAR_score", "N/A"))))
        
        self.patient_table.resizeColumnsToContents()
        layout.addWidget(self.patient_table)
        
        # Selection button
        self.btn_select = QPushButton("Load Selected Patient")
        self.btn_select.clicked.connect(self.select_patient)
        layout.addWidget(self.btn_select)

    def select_patient(self):
        """
        Gets the selected row, finds the corresponding patient data,
        emits the patient_selected signal, and closes the dialog.
        """
        selected_rows = self.patient_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient from the list.")
            return
            
        # Get the index of the selected row
        selected_row_index = selected_rows[0].row()
        
        # Retrieve the full data for the selected patient
        selected_patient_data = self.patients_data[selected_row_index]
        
        # Emit the signal with the patient's data
        self.patient_selected.emit(selected_patient_data)
        
        # Close the dialog
        self.accept()