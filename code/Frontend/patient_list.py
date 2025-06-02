# Add this code to the patient_list.py file, around line 10
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QComboBox, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class PatientListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Patient List")
        self.setGeometry(100, 100, 800, 600)

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

        # Main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.setCentralWidget(self.main_widget)
        
        # Patient table setup
        self.patient_table = QTableWidget()
        self.patient_table.setRowCount(0)
        self.patient_table.setColumnCount(4)
        self.patient_table.setHorizontalHeaderLabels(["id","Patient Name","Pre_PAR_Score","Post_PAR_Score"])
        self.patient_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Set selection behavior and mode
        self.patient_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.patient_table.setSelectionMode(QTableWidget.SingleSelection)


        # Add a separator between the header and data rows
        self.patient_table.setStyleSheet("""
QTableWidget {
    background-color: white;
    gridline-color: #e0e0e0;
}
QTableWidget::item {
    border-bottom: 1px solid #e0e0e0;
    color: black;
}
QTableWidget::item:selected {
    background-color: #1770cb;
    color: white;
}
QHeaderView::section {
    background-color: #f0f0f0;
    border: 1px solid #d0d0d0;
    padding: 4px;
}
""")

        # Connect the cell selection to a function to select the entire row
        self.patient_table.itemSelectionChanged.connect(self.select_entire_row)

        # Add the patient table to the main layout
        self.main_layout.addWidget(self.patient_table)
        self.main_widget.setLayout(self.main_layout)
        
        # View Points Button
        self.btn_view_points = QPushButton("Select Patient")
        self.btn_view_points.setStyleSheet(button_style)
        self.main_layout.addWidget(self.btn_view_points)

    def select_entire_row(self):
        selected_items = self.patient_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            
            # Block signals temporarily to avoid recursion
            self.patient_table.blockSignals(True)
            self.patient_table.selectRow(row)
            self.patient_table.blockSignals(False)
            
            # Print the row data once
            row_texts = [self.patient_table.item(row, col).text() for col in range(self.patient_table.columnCount())]
