from PyQt5.QtWidgets import QFileIconProvider, QStyle, QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QToolTip, QListWidget, QListWidgetItem, QCheckBox
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtCore import Qt, QFileInfo
from pathlib import Path
import os
import sys
import shutil


class BackupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

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

        # Create QListWidgets for file selection after analysis (+ labels)
        files_in_source_label = QLabel('Files only in source directory')
        files_in_backup_label = QLabel('Files only in backup directory')
        self.files_in_source_list = QListWidget(self)
        self.files_in_backup_list = QListWidget(self)

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

        ## container for QListWidgets
        vbox_list_source = QVBoxLayout()
        vbox_list_source.addWidget(files_in_source_label)
        vbox_list_source.addWidget(self.files_in_source_list)
        vbox_list_backup = QVBoxLayout()
        vbox_list_backup.addWidget(files_in_backup_label)
        vbox_list_backup.addWidget(self.files_in_backup_list)
        hbox_files_lists = QHBoxLayout()
        hbox_files_lists.addLayout(vbox_list_source)
        hbox_files_lists.addLayout(vbox_list_backup)
        vbox.addLayout(hbox_files_lists)

        ## backup button
        vbox.addWidget(self.backup_button)

        self.setLayout(vbox)

        # Set window properties
        self.setWindowTitle('Backup Application')
        self.setGeometry(100, 100, 600, 150)
        self.show()

    def get_directory_to_backup(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory to Backup')
        if directory:
            self.dir_line_edit.setText(directory)
            self.backup_button.setEnabled(False)

    def get_backup_location(self):
        backup_location = QFileDialog.getExistingDirectory(self, 'Select Backup Location')
        if backup_location:
            self.backup_line_edit.setText(backup_location)
            self.backup_button.setEnabled(False)

    unique_files_dir = []
    unique_files_backup = []
    different_dates = []
    # common_folders = []
    unique_folders_dir = []
    unique_folders_backup = []

    def analyze(self):
        # Get paths
        directory = self.dir_line_edit.text()
        backup = self.backup_line_edit.text()
        if not (directory and backup):
            return
        
        self.directory_path = Path(directory)
        self.backup_path = Path(backup)

        # Clear contents of files lists
        for file_list in [self.unique_files_dir, self.unique_files_backup, self.different_dates, self.unique_folders_dir, self.unique_folders_backup]:
            file_list.clear()
        
        # Commpare the two directories
        self.compare(self.directory_path, self.backup_path)

        # Update QListWidgets
        self.update_files_lists()
        
        # Enable backup button
        self.backup_button.setEnabled(True)

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

        print('\ncomparing', str(path1), 'and', str(path2))
        print(self.unique_files_dir, '\n', self.unique_files_backup, '\n', self.unique_folders_dir, '\n', self.unique_folders_backup, '\n', self.different_dates)

        # Common folders
        common_folders = [(folders1[folder_name], folders2[folder_name]) for folder_name in folders1 if folder_name in folders2]
        # self.common_folders.extend(common_folders)
        for folder1, folder2 in common_folders:
            self.compare(folder1, folder2)

    def update_files_lists(self):
        # Clear existing items
        self.files_in_source_list.clear()
        self.files_in_backup_list.clear()

        # Update files only in source directory list
        for file in self.unique_files_dir:
            item = self.create_list_item(file, self.directory_path, self.files_in_source_list, checked=True)

        # Update files only in backup directory list
        for file in self.unique_files_backup:
            item = self.create_list_item(file, self.backup_path, self.files_in_backup_list)

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
    
    def backup(self):
        # # Copy all folders (and their contents) that are not present in the backup
        # for folder in self.unique_folders_dir:
        #     relative_path = folder.relative_to(self.directory_path)
        #     destination_path = self.backup_path / relative_path
        #     shutil.copytree(folder, destination_path)

        # # Copy all files that are not present in the backup
        # for file in self.unique_files_dir:
        #     relative_path = file.relative_to(self.directory_path)
        #     destination_path = self.backup_path / relative_path.parent
        #     shutil.copy2(file, destination_path)

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


def run_app():
    app = QApplication(sys.argv)
    window = BackupApp()
    sys.exit(app.exec_())




if __name__ == '__main__':
    run_app()

