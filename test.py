import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHBoxLayout, QWidget, QHeaderView, QAbstractScrollArea
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QFileIconProvider
from PyQt5.QtWidgets import QStyle
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QFont





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Table Example")
        self.setGeometry(500, 500, 1600, 500)  # Set the size of the window to be small in height

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
        icon = QIcon('pd.jpg')
        table.setHorizontalHeaderItem(2, QTableWidgetItem(icon, " "))
        table.horizontalHeaderItem(2).setToolTip("This is the third header")
        

        header = table.horizontalHeader()
        stylesheet = "::section{Background-color:rgb(240,240,240)}"
        table.horizontalHeader().setStyleSheet(stylesheet)
        
        

        # Fill the table with items
        for i in range(rows):  # Assuming 50 rows for example
            fileInfo = QFileInfo(str('improvements.txt'))
            iconProvider = QFileIconProvider()
            icon = iconProvider.icon(fileInfo)
            my_str = f"Itemuitcckyfcyfxtdxzuetxiytcfucoiuyfitfy {i}"
            my_str = ''.join([c + '\u200B' for c in my_str]) #add zero-width space character after every character for word breaking
            table.setItem(i, 0, QTableWidgetItem(icon,my_str))

            table.setItem(i, 1, QTableWidgetItem('28/10/1098'))
            font = QFont()
            font.setBold(True)
            table.item(i, 1).setFont(font)

            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            table.setItem(i, 2, checkbox_item)
                

            

        # Make the table headers visible and fit the contents
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Dynamically adjust column width to fit the window width
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        default_font = QApplication.font()
        fm = QFontMetrics(default_font)  # Create a QFontMetrics object with the specified font
        text = "Last modified in backup"  # Your string
        width = int(fm.width(text)*1.1)  # Get the width of the text in pixels
        table.horizontalHeader().resizeSection(1, int(width*1.1))

        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        scrollbar_width = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        table.horizontalHeader().resizeSection(2, int(scrollbar_width*1.1))

        # Make cells and headers behave like labels (not clickable, focusable, etc.)
        table.setFocusPolicy(Qt.NoFocus)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.horizontalHeader().setSectionsClickable(False)
        table.verticalHeader().setSectionsClickable(False)
        table.verticalHeader().setVisible(False)

        table.setShowGrid(False)
        table.setFrameShape(QFrame.NoFrame)


        self.layout.addWidget(table)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
