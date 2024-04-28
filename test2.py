from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QVBoxLayout, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QCheckBox, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt



class CustomHeaderView(QHeaderView):
    def __init__(self, icon_mapping, text_mapping):
        super().__init__(Qt.Horizontal)
        self.icon_mapping = icon_mapping
        self.text_mapping = text_mapping

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        # super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex in self.icon_mapping:
            icon = QIcon(self.icon_mapping[logicalIndex])
            option = self.viewOptions()
            icon.paint(painter, rect, Qt.AlignRight, QIcon.Normal, QIcon.On)

        if logicalIndex in self.text_mapping:
            text = self.text_mapping[logicalIndex]
            painter.drawText(rect, Qt.AlignCenter, text)

        # painter.restore()

class CheckBoxTableWidgetItem(QTableWidgetItem):
    def __init__(self, checked=False):
        super().__init__()

        self.checkbox_widget = QWidget()
        layout = QHBoxLayout(self.checkbox_widget)
        layout.setAlignment(Qt.AlignRight)  # Align checkbox to the right

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)
        layout.addWidget(self.checkbox)

        # Set the widget as the cell widget
        self.setData(Qt.DisplayRole, None)  # Remove the default text from the cell
        self.setData(Qt.EditRole, None)
        self.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        self.setCheckState(Qt.Unchecked)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.tables = []

        self.setup_tables()

        layout = QVBoxLayout()
        for table in self.tables:
            layout.addWidget(table)
        self.setLayout(layout)

    def setup_tables(self):
        # Define icon mappings and text mappings for each table
        icon_mappings = [
            {0: "keep_in_backup.png", 2: "keep_in_source.png"},  # Example: Icons for columns 0 and 2
            {1: "move_to_backup.png", 3: "move_to_source.png"},  # Example: Icons for columns 1 and 3
            # Add more mappings as needed for additional tables
        ]

        text_mappings = [
            {1: "Header 1", 3: "Header 2"},  # Example: Text for columns 0 and 1
            {0: "Header 3", 2: "Header 4"},  # Example: Text for columns 2 and 3
            # Add more mappings as needed for additional tables
        ]

        for icon_mapping, text_mapping in zip(icon_mappings, text_mappings):
            table = QTableWidget()
            table.setColumnCount(4)  # Example: Create a table with 4 columns
            table.setRowCount(3)
            header = CustomHeaderView(icon_mapping, text_mapping)
            table.setHorizontalHeader(header)

            # Set alignment for other columns
            for i in range(table.columnCount()):
                if i not in icon_mapping and i not in text_mapping:
                    for j in range(table.rowCount()):
                        item = table.item(j, i)
                        if item is not None:
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Add checkboxes
            for i in range(table.rowCount()):
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setAlignment(Qt.AlignRight)  # Align checkbox to the right
                layout.setContentsMargins(0, 0, 0, 0)

                # Create the checkbox
                checkbox = QCheckBox()
                layout.addWidget(checkbox)

                # Set the widget as the cell widget for the current item
                table.setCellWidget(i, 1, widget)

            checkbox = table.cellWidget(1, 1).findChild(QCheckBox)
            if not checkbox.isChecked():
                checkbox.setChecked(True)

            self.tables.append(table)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




icon_mappings = [
            {0: "keep_in_backup.png", 2: "keep_in_source.png"},  # Example: Icons for columns 0 and 2
            {1: "move_to_backup.png", 3: "move_to_source.png"},  # Example: Icons for columns 1 and 3
            # Add more mappings as needed for additional tables
        ]

text_mappings = [
            {1: "Header 1", 3: "Header 2"},  # Example: Text for columns 0 and 1
            {0: "Header 3", 2: "Header 4"},  # Example: Text for columns 2 and 3
            # Add more mappings as needed for additional tables
        ]
