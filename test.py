import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHBoxLayout, QWidget, QHeaderView, QAbstractScrollArea
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Table Example")
        self.setGeometry(500, 500, 1000, 500)  # Set the size of the window to be small in height

        # Create Table
        

        # Set the layout
        self.layout = QHBoxLayout()
        self.createTable(50)
        self.createTable(20)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def createTable(self, rows):
        table = QTableWidget()

        # Set size of table
        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        table.setRowCount(rows)  # Many rows
        table.setColumnCount(3)  # Example column count

        # Set the table headers
        table.setHorizontalHeaderLabels(["Header 1", "Header 2", "Header 3"])
        # Inside the createTable method
        icon = QIcon('pd.jpg')
        table.setHorizontalHeaderItem(2, QTableWidgetItem(icon, " "))
        table.horizontalHeaderItem(2).setToolTip("This is the third header")

        header = table.horizontalHeader()

        # Fill the table with items
        for i in range(rows):  # Assuming 50 rows for example
            for j in range(3):  # Assuming 3 columns for example
                my_str = f"Itemuitcckyfcyfxtdxzuetxiytcfucoiuyfitfy {i},{j}"
                my_str = ''.join([c + '\u200B' for c in my_str]) #add zero-width space character after every character for word breaking
                table.setItem(i, j, QTableWidgetItem(my_str))

        # Make the table headers visible and fit the contents
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Dynamically adjust column width to fit the window width
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Make cells and headers behave like labels (not clickable, focusable, etc.)
        table.setFocusPolicy(Qt.NoFocus)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.horizontalHeader().setSectionsClickable(False)
        table.verticalHeader().setSectionsClickable(False)
        table.verticalHeader().setVisible(False)


        self.layout.addWidget(table)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
