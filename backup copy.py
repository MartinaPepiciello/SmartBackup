from PyQt5.QtWidgets import QFileIconProvider, QDesktopWidget, QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QToolTip, QListWidget, QListWidgetItem, QCheckBox
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtCore import Qt, QFileInfo
from datetime import datetime
from pathlib import Path
import os
import sys
import shutil


class BackupApp(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()


    def init_ui(self):

        # Crearte bold section titles
        directories_title = QLabel('Choose the source and backup directories')
        files_title = QLabel('Choose which files to backup')
        title_font = QFont()
        # title_font.setBold(True)
        title_font.setPointSize(12)
        directories_title.setFont(title_font)
        files_title.setFont(title_font)
        
        # Create line edits for folder locations (+ labels)
        dir_label = QLabel('Directory to backup:')
        backup_label = QLabel('Backup location:')
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

        # Create QListWidgets for folder selection after analysis (+ labels)
        folders_in_source_label = QLabel('Folders only in source directory')
        folders_in_backup_label = QLabel('Folders only in backup directory')
        self.folders_in_source_list = QListWidget(self)
        self.folders_in_backup_list = QListWidget(self)

        # Create QListWidgets for file selection after analysis (+ labels)
        files_in_source_label = QLabel('Files only in source directory')
        files_in_backup_label = QLabel('Files only in backup directory')
        self.files_in_source_list = QListWidget(self)
        self.files_in_backup_list = QListWidget(self)

        # Create QListWidget for files with different dates modified (+ label)
        files_dates_label = QLabel('Files with different dates modified')
        self.files_dates_list = QListWidget(self)

        # Create Backup button
        self.backup_button = QPushButton('Backup')
        self.backup_button.clicked.connect(self.backup)
        self.backup_button.setEnabled(False)
        
        def show_popup(event):
            if not self.backup_button.isEnabled():
                QToolTip.showText(QCursor.pos(), "Please analyze the folders first!")
                
        self.backup_button.setMouseTracking(True)
        self.backup_button.enterEvent = show_popup

        # Arrange widgets using layouts
        ## global container
        vbox = QVBoxLayout()

        ## directories title
        vbox.addWidget(directories_title)
        
        ## containers for folder selectors
        hbox_dir = QHBoxLayout()
        hbox_dir.addWidget(dir_label)
        hbox_dir.addWidget(self.dir_line_edit)
        hbox_dir.addWidget(dir_browse)

        hbox_backup = QHBoxLayout()
        hbox_backup.addWidget(backup_label)
        hbox_backup.addWidget(self.backup_line_edit)
        hbox_backup.addWidget(backup_browse)

        ## container for hbox_dir and hbox_backup
        vbox_browse = QVBoxLayout()
        vbox_browse.addLayout(hbox_dir)
        vbox_browse.addLayout(hbox_backup)

        ## container for vbox_browse and analyze button
        hbox_analyze = QHBoxLayout()
        hbox_analyze.addLayout(vbox_browse)
        hbox_analyze.addWidget(analyze_button)
        vbox.addLayout(hbox_analyze)

        ## files to backup title
        vbox.addWidget(files_title)
        files_title.setContentsMargins(0, 40, 0, 0)

        ## container for QListWidgets (folders)
        vbox_list_folders_source = QVBoxLayout()
        vbox_list_folders_source.addWidget(folders_in_source_label)
        vbox_list_folders_source.addWidget(self.folders_in_source_list)
        vbox_list_folders_backup = QVBoxLayout()
        vbox_list_folders_backup.addWidget(folders_in_backup_label)
        vbox_list_folders_backup.addWidget(self.folders_in_backup_list)
        hbox_folders_lists = QHBoxLayout()
        hbox_folders_lists.addLayout(vbox_list_folders_source)
        hbox_folders_lists.addLayout(vbox_list_folders_backup)
        vbox.addLayout(hbox_folders_lists)

        ## container for QListWidgets (files)
        vbox_list_files_source = QVBoxLayout()
        vbox_list_files_source.addWidget(files_in_source_label)
        vbox_list_files_source.addWidget(self.files_in_source_list)
        vbox_list_files_backup = QVBoxLayout()
        vbox_list_files_backup.addWidget(files_in_backup_label)
        vbox_list_files_backup.addWidget(self.files_in_backup_list)
        hbox_files_lists = QHBoxLayout()
        hbox_files_lists.addLayout(vbox_list_files_source)
        hbox_files_lists.addLayout(vbox_list_files_backup)
        vbox.addLayout(hbox_files_lists)

        ## container for QListWidget of files with different dates
        vbox_list_files_date = QVBoxLayout()
        vbox_list_files_date.addWidget(files_dates_label)
        vbox_list_files_date.addWidget(self.files_dates_list)
        vbox.addLayout(vbox_list_files_date)

        ## backup button
        vbox.addWidget(self.backup_button)

        self.setLayout(vbox)

        # Set window properties
        desktop = QDesktopWidget().screenGeometry()
        width = int(desktop.width() * 0.5)
        height = int(desktop.height() * 0.8)
        self.setWindowTitle('Backup Application')
        self.setGeometry(100, 100, width, height)
        self.show()


    # File explorer for source directory
    def get_directory_to_backup(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory to Backup')
        if directory:
            self.dir_line_edit.setText(directory)
            self.backup_button.setEnabled(False)


    # File explorer for backup directory
    def get_backup_location(self):
        backup_location = QFileDialog.getExistingDirectory(self, 'Select Backup Location')
        if backup_location:
            self.backup_line_edit.setText(backup_location)
            self.backup_button.setEnabled(False)


    # Lists of paths for user decision
    unique_files_dir = []
    unique_files_backup = []
    different_dates = []
    # common_folders = []
    unique_folders_dir = []
    unique_folders_backup = []


    # Compare source and backup directory to find differences
    def analyze(self):
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
        
        # Commpare the two directories
        self.compare(self.directory_path, self.backup_path)

        # Update QListWidgets
        self.update_paths_lists()
        
        # Enable backup button
        self.backup_button.setEnabled(True)

    
    # Recursively compare two directories
    def compare(self, path1, path2):
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

        # print('\ncomparing', str(path1), 'and', str(path2))
        # print(self.unique_files_dir, '\n', self.unique_files_backup, '\n', self.unique_folders_dir, '\n', self.unique_folders_backup, '\n', self.different_dates)

        # Common folders
        common_folders = [(folders1[folder_name], folders2[folder_name]) for folder_name in folders1 if folder_name in folders2]
        # self.common_folders.extend(common_folders)
        for folder1, folder2 in common_folders:
            self.compare(folder1, folder2)

    
    # Show paths for user decision in the UI
    def update_paths_lists(self):
        # Clear existing items
        self.folders_in_source_list.clear()
        self.folders_in_backup_list.clear()
        self.files_in_source_list.clear()
        self.files_in_backup_list.clear()
        self.files_dates_list.clear()

        # Update folders only in source directory list
        for folder in self.unique_folders_dir:
            item = self.create_list_item(folder, self.directory_path, self.folders_in_source_list, checked=True)

        # Update folders only in backup directory list
        for folder in self.unique_folders_backup:
            item = self.create_list_item(folder, self.backup_path, self.folders_in_backup_list)
        
        # Update files only in source directory list
        for file in self.unique_files_dir:
            item = self.create_list_item(file, self.directory_path, self.files_in_source_list, checked=True)

        # Update files only in backup directory list
        for file in self.unique_files_backup:
            item = self.create_list_item(file, self.backup_path, self.files_in_backup_list)

        # Update files with different dates list
        for file in self.different_dates:
            item = self.create_list_item_date(file[0], self.directory_path, file[2], file[3])


    # Create basic path list item for the UI, including icon, relative path and checkbox
    def create_list_item(self, file_path, base_path, scroll_list, checked=False):
        # Create a custom widget for each list item
        item_widget = QWidget()

        # System icon for the file
        fileInfo = QFileInfo(str(file_path))
        iconProvider = QFileIconProvider()
        icon = iconProvider.icon(fileInfo)

        # Relative path label
        relative_path_label = QLabel(str(file_path.relative_to(base_path)))

        # Checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(checked)

        # Arrange widgets in the custom widget
        hbox_item = QHBoxLayout(item_widget)
        hbox_item.addWidget(relative_path_label)
        hbox_item.addWidget(checkbox, alignment=Qt.AlignRight)

        # Create QListWidgetItem with the custom widget
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())  # Set the size hint for proper layout
        list_item.setIcon(icon)

        scroll_list.addItem(list_item)
        scroll_list.setItemWidget(list_item, item_widget)
    

    # Create path list item to compare dates modified
    def create_list_item_date(self, file_path, base_path, date_edited1, date_edited2):
        # Create a custom widget for each list item
        item_widget = QWidget()

        # System icon for the file
        fileInfo = QFileInfo(str(file_path))
        iconProvider = QFileIconProvider()
        icon = iconProvider.icon(fileInfo)

        # Relative path label
        relative_path_label = QLabel(str(file_path.relative_to(base_path)))

        # Check the checkbox corresponding to the most recent date
        checked = date_edited1 > date_edited2

        # Checkboxes
        checkbox1 = QCheckBox()
        checkbox2 = QCheckBox()
        checkbox1.setChecked(checked)
        checkbox2.setChecked(not checked)

        # Date labels
        date_dt1 = datetime.utcfromtimestamp(date_edited1)
        date_dt2 = datetime.utcfromtimestamp(date_edited2)
        date_label1 = QLabel(date_dt1.strftime("%d/%m/%Y %H:%M"))
        date_label2 = QLabel(date_dt2.strftime("%d/%m/%Y %H:%M"))

        # Most recent date in bold
        font1 = QFont()
        font2 = QFont()
        font1.setBold(checked)
        font2.setBold(not checked)
        date_label1.setFont(font1)
        date_label2.setFont(font2)

        # Arrange widgets in the custom widget
        hbox_item = QHBoxLayout(item_widget)
        hbox_item.addWidget(relative_path_label)
        hbox_item.addWidget(checkbox1, alignment=Qt.AlignRight)
        hbox_item.addWidget(date_label1)
        hbox_item.addWidget(checkbox2, alignment=Qt.AlignRight)
        hbox_item.addWidget(date_label2)

        # Create QListWidgetItem with the custom widget
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())  # Set the size hint for proper layout
        list_item.setIcon(icon)

        self.files_dates_list.addItem(list_item)
        self.files_dates_list.setItemWidget(list_item, item_widget)
    
    
    # Perform copy of selected items to backup and delete unselected items from backup
    def backup(self):
        # # Copy all folders (and their contents) that are not present in the backup
        # for folder in self.unique_folders_dir:
            # relative_path = folder.relative_to(self.directory_path)
            # destination_path = self.backup_path / relative_path
            # shutil.copytree(folder, destination_path)

        # # Copy all files that are not present in the backup
        # for file in self.unique_files_dir:
        #     relative_path = file.relative_to(self.directory_path)
        #     destination_path = self.backup_path / relative_path.parent
        #     shutil.copy2(file, destination_path)

        # Perform backup for folders in source directory
        for i, folder in enumerate(self.unique_folders_dir):
            item = self.folders_in_source_list.item(i)
            checkbox = self.folders_in_source_list.itemWidget(item).findChild(QCheckBox)
            if checkbox.isChecked():
                relative_path = folder.relative_to(self.directory_path)
                destination_path = self.backup_path / relative_path
                shutil.copytree(folder, destination_path)    

        # Remove folders from backup directory
        for i, folder in enumerate(self.unique_folders_backup):
            item = self.folders_in_backup_list.item(i)
            checkbox = self.folders_in_backup_list.itemWidget(item).findChild(QCheckBox)
            if not checkbox.isChecked():
                shutil.rmtree(folder)
        
        # Perform backup for files in source directory
        for i, file in enumerate(self.unique_files_dir):
            item = self.files_in_source_list.item(i)
            checkbox = self.files_in_source_list.itemWidget(item).findChild(QCheckBox)
            if checkbox.isChecked():
                relative_path = file.relative_to(self.directory_path)
                destination_path = self.backup_path / relative_path.parent
                shutil.copy2(file, destination_path)    

        # Remove files from backup directory
        for i, file in enumerate(self.unique_files_backup):
            item = self.files_in_backup_list.item(i)
            checkbox = self.files_in_backup_list.itemWidget(item).findChild(QCheckBox)
            if not checkbox.isChecked():
                os.remove(file)

        # Files with different dates edited
        for i, file in enumerate(self.different_dates):
            path1, path2, date1, date2 = file
            item = self.files_dates_list.item(i)
            widget = self.files_dates_list.itemWidget(item)
            checkbox1, checkbox2 = [child for child in widget.children() if isinstance(child, QCheckBox)]

            # if both checkboxes are checked, save both files to backup with a suffix specifying the date modified
            if checkbox1.isChecked() and checkbox2.isChecked():
                date_dt1 = datetime.utcfromtimestamp(date1)
                date_dt2 = datetime.utcfromtimestamp(date2)
                date_suffix1 = date_dt1.strftime("(%d-%m-%Y--%H-%M)")
                date_suffix2 = date_dt2.strftime("(%d-%m-%Y--%H-%M)")

                directory2, filename2 = os.path.split(path2)
                new_filename2 = f"{os.path.splitext(filename2)[0]}{date_suffix2}{os.path.splitext(filename2)[1]}"
                new_path2 = os.path.join(directory2, new_filename2)
                os.rename(path2, new_path2)

                directory1, filename1 = os.path.split(path1)
                new_filename1 = f"{os.path.splitext(filename1)[0]}{date_suffix1}{os.path.splitext(filename1)[1]}"
                new_path1 = os.path.join(directory2, new_filename1)
                shutil.copy2(path1, new_path1)

            # if only checkbox1 is checked, delete existing file from backup and save file from source instead
            elif checkbox1.isChecked() and not checkbox2.isChecked():
                os.remove(path2)
                relative_path = path1.relative_to(self.directory_path)
                destination_path = self.backup_path / relative_path.parent
                shutil.copy2(path1, destination_path)

            # if only checkbox2 is checked, overwrite source version with backup version
            elif not checkbox1.isChecked() and checkbox2.isChecked():
                os.remove(path1)
                relative_path = path2.relative_to(self.backup_path)
                destination_path = self.directory_path / relative_path.parent
                shutil.copy2(path2, destination_path)

            # if no checkbox is checked, just delete existing file from backup
            else:
                os.remove(path2)




def run_app():
    app = QApplication(sys.argv)
    window = BackupApp()
    sys.exit(app.exec_())




if __name__ == '__main__':
    run_app()

