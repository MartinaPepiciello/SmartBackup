from datetime import datetime, timezone, timedelta
import os
from pathlib import Path
from PyQt5.QtCore import Qt, QFileInfo, QSize
from PyQt5.QtGui import QCursor, QFont, QFontMetrics, QIcon
from PyQt5.QtWidgets import QAbstractScrollArea, QApplication, QCheckBox, QDesktopWidget, QFileDialog, QFileIconProvider, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QProgressBar, QStyle, QTableWidget, QTableWidgetItem, QToolTip, QVBoxLayout, QWidget
import shutil
import sys




class BackupApp(QWidget):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()


    def init_ui(self):
        '''
        Initialize the UI
        '''

        # Get width of a scrollbar to use as spacing unit
        scrollbar_width = self.app.style().pixelMetric(QStyle.PM_ScrollBarExtent)

        # Get width of text for table column sizing
        default_font = QApplication.font()
        default_font.setBold(True)
        fm = QFontMetrics(default_font)
        date_width = fm.width('Last modified in backup  ')

        # Crearte section titles
        directories_title = QLabel('Choose the source and backup directories')
        files_title = QLabel('Choose which files to backup')
        title_font = QFont()
        title_font.setPointSize(12)
        directories_title.setFont(title_font)
        files_title.setFont(title_font)
        
        # Create line edits for folder locations
        self.dir_line_edit = QLineEdit()
        self.backup_line_edit = QLineEdit()

        # Create buttons for browsing
        dir_browse = QPushButton('Browse')
        dir_browse.clicked.connect(self.get_directory_to_backup)
        backup_browse = QPushButton('Browse')
        backup_browse.clicked.connect(self.get_backup_location)

        # Create Analyze button
        analyze_button = QPushButton('Analyze')
        analyze_button.clicked.connect(self.analyze)

        # Create label to show which folder is being analyzed
        self.analyzing_label = QLabel(' ')

        # Create QTableWidgets for folder selection after analysis (folders only in source)
        self.folders_in_source_table = QTableWidget()
        self.folders_in_source_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.folders_in_source_table.setRowCount(1)
        self.folders_in_source_table.setColumnCount(3)
        self.folders_in_source_table.setHorizontalHeaderLabels(['Folders only in source directory', '', ''])
        keep_in_src_icon = QIcon('keep_in_source.png')
        self.folders_in_source_table.setHorizontalHeaderItem(1, QTableWidgetItem(keep_in_src_icon, ''))
        self.folders_in_source_table.horizontalHeaderItem(1).setToolTip('Checked folders and their contents will remain in the source')
        move_to_bk_icon = QIcon('move_to_backup.png')
        self.folders_in_source_table.setHorizontalHeaderItem(2, QTableWidgetItem(move_to_bk_icon, ''))
        self.folders_in_source_table.horizontalHeaderItem(2).setToolTip('Checked folders and their contents will be copied to backup')
        self.style_table(self.folders_in_source_table)
        self.folders_in_source_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.folders_in_source_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.folders_in_source_table.horizontalHeader().resizeSection(1, scrollbar_width)
        self.folders_in_source_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.folders_in_source_table.horizontalHeader().resizeSection(2, scrollbar_width)

        # Create QTableWidgets for folder selection after analysis (folders only in backup)
        self.folders_in_backup_table = QTableWidget()
        self.folders_in_backup_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.folders_in_backup_table.setRowCount(1)
        self.folders_in_backup_table.setColumnCount(3)
        self.folders_in_backup_table.setHorizontalHeaderLabels(['Folders only in backup directory', '', ''])
        keep_in_bk_icon = QIcon('keep_in_backup.png')
        self.folders_in_backup_table.setHorizontalHeaderItem(1, QTableWidgetItem(keep_in_bk_icon, ''))
        self.folders_in_backup_table.horizontalHeaderItem(1).setToolTip('Checked folders and their contents will remain in backup')
        move_to_src_icon = QIcon('move_to_source.png')
        self.folders_in_backup_table.setHorizontalHeaderItem(2, QTableWidgetItem(move_to_src_icon, ''))
        self.folders_in_backup_table.horizontalHeaderItem(2).setToolTip('Checked folders and their contents will be copied to source')
        self.style_table(self.folders_in_backup_table)
        self.folders_in_backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.folders_in_backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.folders_in_backup_table.horizontalHeader().resizeSection(1, scrollbar_width)
        self.folders_in_backup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.folders_in_backup_table.horizontalHeader().resizeSection(2, scrollbar_width)

        # Create QTableWidgets for file selection after analysis (files only in source)
        self.files_in_source_table = QTableWidget()
        self.files_in_source_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.files_in_source_table.setRowCount(1)
        self.files_in_source_table.setColumnCount(3)
        self.files_in_source_table.setHorizontalHeaderLabels(['Files only in source directory', '', ''])
        self.files_in_source_table.setHorizontalHeaderItem(1, QTableWidgetItem(keep_in_src_icon, ''))
        self.files_in_source_table.horizontalHeaderItem(1).setToolTip('Checked files and their contents will remain in the source')
        self.files_in_source_table.setHorizontalHeaderItem(2, QTableWidgetItem(move_to_bk_icon, ''))
        self.files_in_source_table.horizontalHeaderItem(2).setToolTip('Checked files and their contents will be copied to backup')
        self.style_table(self.files_in_source_table)
        self.files_in_source_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.files_in_source_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.files_in_source_table.horizontalHeader().resizeSection(1, scrollbar_width)
        self.files_in_source_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.files_in_source_table.horizontalHeader().resizeSection(2, scrollbar_width)

        # Create QTableWidgets for file selection after analysis (file only in backup)
        self.files_in_backup_table = QTableWidget()
        self.files_in_backup_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.files_in_backup_table.setRowCount(1)
        self.files_in_backup_table.setColumnCount(3)
        self.files_in_backup_table.setHorizontalHeaderLabels(['Files only in backup directory', '', ''])
        self.files_in_backup_table.setHorizontalHeaderItem(1, QTableWidgetItem(keep_in_bk_icon, ''))
        self.files_in_backup_table.horizontalHeaderItem(1).setToolTip('Checked files and their contents will remain in backup')
        self.files_in_backup_table.setHorizontalHeaderItem(2, QTableWidgetItem(move_to_src_icon, ''))
        self.files_in_backup_table.horizontalHeaderItem(2).setToolTip('Checked files and their contents will be copied to source')
        self.style_table(self.files_in_backup_table)
        self.files_in_backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.files_in_backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.files_in_backup_table.horizontalHeader().resizeSection(1, scrollbar_width)
        self.files_in_backup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.files_in_backup_table.horizontalHeader().resizeSection(2, scrollbar_width)

        # Create QListWidget for files with different dates modified
        self.files_dates_table = QTableWidget()
        self.files_dates_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.files_dates_table.setRowCount(1)
        self.files_dates_table.setColumnCount(7)
        self.files_dates_table.setHorizontalHeaderLabels(['Files with different dates modified', '', '', 'Last modified in source', '', '', 'Last modified in backup'])
        self.files_dates_table.setHorizontalHeaderItem(1, QTableWidgetItem(keep_in_src_icon, ''))
        self.files_dates_table.horizontalHeaderItem(1).setToolTip('Checked files and their contents will remain in the source')
        self.files_dates_table.setHorizontalHeaderItem(2, QTableWidgetItem(move_to_bk_icon, ''))
        self.files_dates_table.horizontalHeaderItem(2).setToolTip('Checked files and their contents will be copied to backup')
        self.files_dates_table.setHorizontalHeaderItem(4, QTableWidgetItem(keep_in_bk_icon, ''))
        self.files_dates_table.horizontalHeaderItem(4).setToolTip('Checked files and their contents will remain in backup')
        self.files_dates_table.setHorizontalHeaderItem(5, QTableWidgetItem(move_to_src_icon, ''))
        self.files_dates_table.horizontalHeaderItem(5).setToolTip('Checked files and their contents will be copied to source')
        self.style_table(self.files_dates_table)
        self.files_dates_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 7):
            self.files_dates_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
            self.files_dates_table.horizontalHeader().resizeSection(i, scrollbar_width)
        self.files_dates_table.horizontalHeader().resizeSection(3, date_width)
        self.files_dates_table.horizontalHeader().resizeSection(6, date_width)

        # Create Backup button
        self.backup_button = QPushButton('Backup')
        self.backup_button.clicked.connect(self.backup)
        self.backup_button.setEnabled(False)
        
        def show_popup(event):
            if not self.backup_button.isEnabled():
                QToolTip.showText(QCursor.pos(), "Please analyze the folders first!")
                
        self.backup_button.setMouseTracking(True)
        self.backup_button.enterEvent = show_popup

        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)


        # Arrange widgets using layouts
        #  global container
        vbox = QVBoxLayout()

        #  directories title
        vbox.addWidget(directories_title)
        
        #  containers for folder selectors
        hbox_dir = QHBoxLayout()
        hbox_dir.addWidget(QLabel('Directory to backup:'))
        hbox_dir.addWidget(self.dir_line_edit)
        hbox_dir.addWidget(dir_browse)
        hbox_backup = QHBoxLayout()
        hbox_backup.addWidget(QLabel('Backup location:'))
        hbox_backup.addWidget(self.backup_line_edit)
        hbox_backup.addWidget(backup_browse)

        #  container for hbox_dir and hbox_backup
        vbox_browse = QVBoxLayout()
        vbox_browse.addLayout(hbox_dir)
        vbox_browse.addLayout(hbox_backup)

        #  container for vbox_browse and analyze button
        hbox_analyze = QHBoxLayout()
        hbox_analyze.addLayout(vbox_browse)
        hbox_analyze.addWidget(analyze_button)
        vbox.addLayout(hbox_analyze)

        #  analyzing label
        vbox.addWidget(self.analyzing_label)

        #  files to backup title
        vbox.addWidget(files_title)
        files_title.setContentsMargins(0, scrollbar_width, 0, 0)

        #  unique folders tables
        hbox_folders_lists = QHBoxLayout()
        hbox_folders_lists.addWidget(self.folders_in_source_table)
        hbox_folders_lists.addWidget(self.folders_in_backup_table)
        hbox_folders_lists.setContentsMargins(0, 0, 0, scrollbar_width)
        vbox.addLayout(hbox_folders_lists)

        #  unique files tables
        hbox_files_lists = QHBoxLayout()
        hbox_files_lists.addWidget(self.files_in_source_table)
        hbox_files_lists.addWidget(self.files_in_backup_table)
        hbox_files_lists.setContentsMargins(0, 0, 0, scrollbar_width)
        vbox.addLayout(hbox_files_lists)

        #  files with different dates
        hbox_list_files_date = QVBoxLayout()
        hbox_list_files_date.addWidget(self.files_dates_table)
        hbox_list_files_date.setContentsMargins(0, 0, 0, scrollbar_width)
        vbox.addLayout(hbox_list_files_date)

        #  backup button and progress bar
        vbox.addWidget(self.backup_button)
        vbox.addWidget(self.progress_bar)

        #  complete layout
        self.setLayout(vbox)

        # Set window properties
        desktop = QDesktopWidget().screenGeometry()
        width = int(desktop.width() * 0.6)
        height = int(desktop.height() * 0.8)
        left = int(desktop.width() * 0.2)
        top = int(desktop.height() * 0.1)
        self.setWindowTitle('Smart Backup')
        self.setGeometry(left, top, width, height)
        self.show()


    def style_table(self, table):
        '''
        Styles common to all tables
        '''
        
        # Set table header color
        header = table.horizontalHeader()
        stylesheet = "::section{Background-color:rgb(240,240,240); border:0}"
        # stylesheet = "::section{Background-color:rgb(240,240,240);}"
        header.setStyleSheet(stylesheet)

        # Make headers fit the contents
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Make vertical scrollbar always visible
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Make cells and headers behave like labels (not clickable, focusable, etc.)
        table.setFocusPolicy(Qt.NoFocus)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.horizontalHeader().setSectionsClickable(False)
        table.verticalHeader().setSectionsClickable(False)

        # Hide vertical header
        table.verticalHeader().setVisible(False)

        # Hide all grids
        table.setShowGrid(False)
        table.setFrameShape(QFrame.NoFrame)
    
    
    def get_directory_to_backup(self):
        '''
        File explorer for source directory
        '''

        directory = QFileDialog.getExistingDirectory(self, 'Select Directory to Backup')
        if directory:
            self.dir_line_edit.setText(directory)
            self.backup_button.setEnabled(False)


    def get_backup_location(self):
        '''
        File explorer for backup directory
        '''

        backup_location = QFileDialog.getExistingDirectory(self, 'Select Backup Location')
        if backup_location:
            self.backup_line_edit.setText(backup_location)
            self.backup_button.setEnabled(False)


    # Lists of paths for user decision
    unique_files_dir = []
    unique_files_backup = []
    unique_folders_dir = []
    unique_folders_backup = []
    different_dates = []


    def analyze(self):
        '''
        Compare source and backup directory to find differences
        '''

        # Get paths
        directory = self.dir_line_edit.text()
        backup = self.backup_line_edit.text()
        if not (directory and backup):
            return
        
        self.directory_path = Path(directory)
        self.backup_path = Path(backup)

        # Clear contents of paths lists
        for file_list in [self.unique_files_dir, self.unique_files_backup, self.different_dates, self.unique_folders_dir, self.unique_folders_backup]:
            file_list.clear()
        
        # Compare the two directories
        self.compare(self.directory_path, self.backup_path)

        # Reset analyzing label
        self.analyzing_label.setText('  ')
        QApplication.processEvents()

        # Update QListWidgets
        self.update_paths_tables()
        
        # Enable backup button
        self.backup_button.setEnabled(True)

    
    def compare(self, path1, path2):
        '''
        Recursively compare two directories
        '''

        # Show which folder is being analyzed
        self.analyzing_label.setText('Analyzing ' + str(path1.relative_to(self.directory_path)))
        QApplication.processEvents()

        # Get files in both paths
        files1 = {file.name: file for file in path1.glob('*') if file.is_file()}
        files2 = {file.name: file for file in path2.glob('*') if file.is_file()}

        # Files in path1 but not in path2
        unique_files1 = [files1[file_name] for file_name in files1 if file_name not in files2]
        self.unique_files_dir.extend(unique_files1)

        # Files in path2 but not in path1
        unique_files2 = [files2[file_name] for file_name in files2 if file_name not in files1]
        self.unique_files_backup.extend(unique_files2)

        # Files in both paths with different date edited
        for file_name, file_path1 in files1.items():
            if file_name in files2:
                file_path2 = files2[file_name]

                date_edited1 = int(os.path.getmtime(file_path1))
                date_edited2 = int(os.path.getmtime(file_path2))

                if date_edited1 != date_edited2:
                    self.different_dates.append((file_path1, file_path2, date_edited1, date_edited2))

        # Get folders in both paths
        folders1 = {folder.name: folder for folder in path1.iterdir() if folder.is_dir()}
        folders2 = {folder.name: folder for folder in path2.iterdir() if folder.is_dir()}

        # Folders in path1 but not in path2
        unique_folders1 = [folders1[folder_name] for folder_name in folders1 if folder_name not in folders2]
        self.unique_folders_dir.extend(unique_folders1)

        # Folders in path2 but not in path1
        unique_folders2 = [folders2[folder_name] for folder_name in folders2 if folder_name not in folders1]
        self.unique_folders_backup.extend(unique_folders2)

        # Common folders (recursively compare)
        common_folders = [(folders1[folder_name], folders2[folder_name]) for folder_name in folders1 if folder_name in folders2]
        for folder1, folder2 in common_folders:
            self.compare(folder1, folder2)

    
    def update_paths_tables(self):
        '''
        Show paths for user decision in the UI
        '''

        # Update folders only in source directory table
        self.folders_in_source_table.setRowCount(len(self.unique_folders_dir))
        for i, folder in enumerate(self.unique_folders_dir):
            self.create_table_item(i, folder, self.directory_path, self.folders_in_source_table, checked=True)

        # Update folders only in backup directory table
        self.folders_in_backup_table.setRowCount(len(self.unique_folders_backup))
        for i, folder in enumerate(self.unique_folders_backup):
            self.create_table_item(i, folder, self.backup_path, self.folders_in_backup_table)
        
        # Update files only in source directory table
        self.files_in_source_table.setRowCount(len(self.unique_files_dir))
        for i, file in enumerate(self.unique_files_dir):
            self.create_table_item(i, file, self.directory_path, self.files_in_source_table, checked=True)

        # Update files only in backup directory table
        self.files_in_backup_table.setRowCount(len(self.unique_files_backup))
        for i, file in enumerate(self.unique_files_backup):
            self.create_table_item(i, file, self.backup_path, self.files_in_backup_table)

        # Update files with different dates list
        self.files_dates_table.setRowCount(len(self.different_dates))
        for i, file in enumerate(self.different_dates):
            self.create_list_item_date(i, file[0], self.directory_path, file[2], file[3])


    def create_table_item(self, row, file_path, base_path, table, checked=False):
        '''
        Create basic path list item for the UI, including icon, relative path and checkbox
        '''

        # System icon for the file
        fileInfo = QFileInfo(str(file_path))
        iconProvider = QFileIconProvider()
        icon = iconProvider.icon(fileInfo)

        # Relative path with zero-width space character after each letter (for word breaking purposes)
        relative_path_str = ''.join([c + '\u200B' for c in str(file_path.relative_to(base_path))])
        table.setItem(row, 0, QTableWidgetItem(icon, relative_path_str))

        # Checkboxes
        checkbox1 = QTableWidgetItem()
        checkbox1.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox1.setCheckState(Qt.Checked)
        table.setItem(row, 1, checkbox1)

        checkbox2 = QTableWidgetItem()
        checkbox2.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox2.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        table.setItem(row, 2, checkbox2)
    

    def create_list_item_date(self, row, file_path, base_path, date_edited1, date_edited2):
        '''
        Create path list item to compare dates modified
        '''

        # System icon for the file
        fileInfo = QFileInfo(str(file_path))
        iconProvider = QFileIconProvider()
        icon = iconProvider.icon(fileInfo)

        # Relative path with zero-width space character after each letter (for word breaking purposes)
        relative_path_str = ''.join([c + '\u200B' for c in str(file_path.relative_to(base_path))])
        self.files_dates_table.setItem(row, 0, QTableWidgetItem(icon, relative_path_str))

        # Check the checkbox corresponding to the most recent date
        checked = date_edited1 > date_edited2

        # Checkboxes
        checkbox1 = QTableWidgetItem()
        checkbox1.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox1.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.files_dates_table.setItem(row, 1, checkbox1)

        checkbox2 = QTableWidgetItem()
        checkbox2.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox2.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.files_dates_table.setItem(row, 2, checkbox2)

        checkbox3 = QTableWidgetItem()
        checkbox3.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox3.setCheckState(Qt.Unchecked if checked else Qt.Checked)
        self.files_dates_table.setItem(row, 4, checkbox3)

        checkbox4 = QTableWidgetItem()
        checkbox4.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox4.setCheckState(Qt.Unchecked if checked else Qt.Checked)
        self.files_dates_table.setItem(row, 5, checkbox4)

        # Dates (most recent in bold)
        date_dt1 = datetime.fromtimestamp(date_edited1, timezone(timedelta(hours=1)))
        self.files_dates_table.setItem(row, 3, QTableWidgetItem(date_dt1.strftime("%d/%m/%Y %H:%M")))
        font1 = QFont()
        font1.setBold(checked)
        self.files_dates_table.item(row, 3).setFont(font1)

        date_dt2 = datetime.fromtimestamp(date_edited2, timezone(timedelta(hours=1)))
        self.files_dates_table.setItem(row, 6, QTableWidgetItem(date_dt2.strftime("%d/%m/%Y %H:%M")))
        font2 = QFont()
        font2.setBold(not checked)
        self.files_dates_table.item(row, 6).setFont(font2)
    
    
    def backup(self):
        '''
        Perform copy of selected items and delete unselected items
        '''

        # Initialize item counter for progress bar
        total_items = len(self.unique_folders_dir) + len(self.unique_folders_backup) + len(self.unique_files_dir) + len(self.unique_files_backup) + len(self.different_dates)
        processed_items = 0

        # Folders in source directory only
        #  checked = [keep in source, copy to backup]
        for i, folder in enumerate(self.unique_folders_dir):
            checked = [self.folders_in_source_table.item(i, col).checkState() == Qt.Checked for col in [1, 2]]
            if checked[1]:
                relative_path = folder.relative_to(self.directory_path) # copy folder to backup
                destination_path = self.backup_path / relative_path
                shutil.copytree(folder, destination_path)
            if not checked[0]:
                shutil.rmtree(folder) # remove folder from source
            processed_items += 1
            self.update_progress(processed_items, total_items)  

        # Folders in backup directory only
        #  checked = [keep in backup, copy to source]
        for i, folder in enumerate(self.unique_folders_backup):
            checked = [self.folders_in_backup_table.item(i, col).checkState() == Qt.Checked for col in [1, 2]]
            if checked[1]:
                relative_path = folder.relative_to(self.backup_path) # copy folder to source
                destination_path = self.directory_path / relative_path
                shutil.copytree(folder, destination_path)
            if not checked[0]:
                shutil.rmtree(folder)
            processed_items += 1
            self.update_progress(processed_items, total_items) 
        
        # Files in source directory only
        #  checked = [keep in source, copy to backup]
        for i, file in enumerate(self.unique_files_dir):
            checked = [self.files_in_source_table.item(i, col).checkState() == Qt.Checked for col in [1, 2]]
            if checked[1]:
                relative_path = file.relative_to(self.directory_path) # copy file to backup
                destination_path = self.backup_path / relative_path.parent
                shutil.copy2(file, destination_path) 
            if not checked[0]:
                os.remove(file) # remove file from source
            processed_items += 1
            self.update_progress(processed_items, total_items)    

        # Files in backup directory only
        #  checked = [keep in backup, copy to source]
        for i, file in enumerate(self.unique_files_backup):
            checked = [self.files_in_backup_table.item(i, col).checkState() == Qt.Checked for col in [1, 2]]
            if checked[1]:
                relative_path = file.relative_to(self.backup_path) # copy file to source
                destination_path = self.directory_path / relative_path.parent
                shutil.copy2(file, destination_path)
            if not checked[0]:
                os.remove(file) # remove file from backup
            processed_items += 1
            self.update_progress(processed_items, total_items) 

        # Files with different dates edited
        #  checked = [keep in source, copy to backup, keep in backup, copy to source]
        for i, file in enumerate(self.different_dates):
            path1, path2, date1, date2 = file
            checked = [self.files_dates_table.item(i, col).checkState() == Qt.Checked for col in [1, 2, 4, 5]]

            if [checked[0], checked[1], checked[3]] == [False, False, False]:
                os.remove(path1)
                if not checked[2]: 
                    os.remove(path2)
            elif checked == [True, False, False, False]:
                os.remove(path2)
            elif [checked[0], checked[1], checked[3]] == [False, False, True]:
                os.remove(path1)
                directory1, filename1 = os.path.split(path1)
                directory2, filename2 = os.path.split(path2)
                new_path2 = os.path.join(directory1, filename2)
                shutil.copy2(path2, new_path2)
                if not checked[2]:
                    os.remove(path2)
            elif checked[1:] == [True, False, False]:
                os.remove(path2)
                directory1, filename1 = os.path.split(path1)
                directory2, filename2 = os.path.split(path2)
                new_path1 = os.path.join(directory2, filename1)
                shutil.copy2(path1, new_path1)
                if not checked[0]:
                    os.remove(path1)
            elif checked[1:] == [True, True, False]:
                date_dt1 = datetime.fromtimestamp(date1, timezone(timedelta(hours=1)))
                date_suffix1 = date_dt1.strftime("%d-%m-%Y_%H-%M")
                directory1, filename1 = os.path.split(path1)
                new_filename1 = f"{os.path.splitext(filename1)[0]}_{date_suffix1}{os.path.splitext(filename1)[1]}"
                date_dt2 = datetime.fromtimestamp(date2, timezone(timedelta(hours=1)))
                date_suffix2 = date_dt2.strftime("%d-%m-%Y_%H-%M")
                directory2, filename2 = os.path.split(path2)
                new_filename2 = f"{os.path.splitext(filename2)[0]}_{date_suffix2}{os.path.splitext(filename2)[1]}"
                new_path1 = os.path.join(directory2, new_filename1)
                new_path2 = os.path.join(directory2, new_filename2)
                os.rename(path2, new_path2)
                shutil.copy2(path1, new_path1)
                if not checked[0]:
                    os.remove(path1)
            elif [checked[0], checked[1], checked[3]] == [True, False, True]:
                date_dt1 = datetime.fromtimestamp(date1, timezone(timedelta(hours=1)))
                date_suffix1 = date_dt1.strftime("%d-%m-%Y_%H-%M")
                directory1, filename1 = os.path.split(path1)
                new_filename1 = f"{os.path.splitext(filename1)[0]}_{date_suffix1}{os.path.splitext(filename1)[1]}"
                date_dt2 = datetime.fromtimestamp(date2, timezone(timedelta(hours=1)))
                date_suffix2 = date_dt2.strftime("%d-%m-%Y_%H-%M")
                directory2, filename2 = os.path.split(path2)
                new_filename2 = f"{os.path.splitext(filename2)[0]}_{date_suffix2}{os.path.splitext(filename2)[1]}"
                new_path1 = os.path.join(directory1, new_filename1)
                new_path2 = os.path.join(directory2, new_filename2)
                os.rename(path1, new_path1)
                shutil.copy2(path2, new_path2)
                if not checked[2]:
                    os.remove(path2)
            elif [checked[0], checked[1], checked[3]] == [True, True, True]:
                date_dt1 = datetime.fromtimestamp(date1, timezone(timedelta(hours=1)))
                date_suffix1 = date_dt1.strftime("%d-%m-%Y_%H-%M")
                directory1, filename1 = os.path.split(path1)
                new_filename1 = f"{os.path.splitext(filename1)[0]}_{date_suffix1}{os.path.splitext(filename1)[1]}"
                date_dt2 = datetime.fromtimestamp(date2, timezone(timedelta(hours=1)))
                date_suffix2 = date_dt2.strftime("%d-%m-%Y_%H-%M")
                directory2, filename2 = os.path.split(path2)
                new_filename2 = f"{os.path.splitext(filename2)[0]}_{date_suffix2}{os.path.splitext(filename2)[1]}"
                new_path1_dir = os.path.join(directory1, new_filename1)
                new_path2_dir = os.path.join(directory1, new_filename2)
                os.rename(path1, new_path1_dir)
                shutil.copy2(path2, new_path2_dir)
                if checked[2]:
                    new_path1_bk = os.path.join(directory2, new_filename1)
                    new_path2_bk = os.path.join(directory2, new_filename2)
                    shutil.copy2(new_path1_dir, new_path1_bk)
                    os.rename(path2, new_path2_bk)
                else:
                    new_path1_bk = os.path.join(directory2, filename1)
                    shutil.copy2(new_path1_dir, new_path1_bk)
                    os.remove(path2)
            elif checked == [False, True, False, True]:
                temp_path = path1.with_name('temp')
                shutil.move(path1, temp_path)
                shutil.move(path2, path1)
                shutil.move(temp_path, path2)
            elif checked == [False, True, True, True]:
                date_dt1 = datetime.fromtimestamp(date1, timezone(timedelta(hours=1)))
                date_suffix1 = date_dt1.strftime("%d-%m-%Y_%H-%M")
                directory1, filename1 = os.path.split(path1)
                new_filename1 = f"{os.path.splitext(filename1)[0]}_{date_suffix1}{os.path.splitext(filename1)[1]}"
                date_dt2 = datetime.fromtimestamp(date2, timezone(timedelta(hours=1)))
                date_suffix2 = date_dt2.strftime("%d-%m-%Y_%H-%M")
                directory2, filename2 = os.path.split(path2)
                new_filename2 = f"{os.path.splitext(filename2)[0]}_{date_suffix2}{os.path.splitext(filename2)[1]}"
                new_path1_bk = os.path.join(directory2, new_filename1)
                new_path2_dir = os.path.join(directory1, filename2)
                new_path2_bk = os.path.join(directory2, new_filename2)
                shutil.copy2(path1, new_path1_bk)
                os.remove(path1)
                shutil.copy2(path2, new_path2_dir)
                os.rename(path2, new_path2_bk)

            processed_items += 1
            self.update_progress(processed_items, total_items) 


    def update_progress(self, processed, total):
        '''
        Update progress bar
        '''

        progress_percentage = int((processed / total) * 100)
        self.progress_bar.setValue(progress_percentage)
        QApplication.processEvents()




def run_app():
    app = QApplication(sys.argv)
    window = BackupApp(app)
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()

