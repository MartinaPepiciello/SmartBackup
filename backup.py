import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog

class BackupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create labels
        dir_label = QLabel('Directory to backup:')
        backup_label = QLabel('Backup location:')

        # Create line edits
        self.dir_line_edit = QLineEdit()
        self.backup_line_edit = QLineEdit()

        # Create buttons for browsing
        dir_button = QPushButton('Browse')
        dir_button.clicked.connect(self.get_directory_to_backup)

        backup_button = QPushButton('Browse')
        backup_button.clicked.connect(self.get_backup_location)

        # Create Analyze button
        analyze_button = QPushButton('Analyze')
        analyze_button.clicked.connect(self.analyze)

        # Arrange widgets using layouts
        ## global container
        vbox = QVBoxLayout()
        
        ## containers for folder selectors
        hbox_dir = QHBoxLayout()
        hbox_dir.addWidget(dir_label)
        hbox_dir.addWidget(self.dir_line_edit)
        hbox_dir.addWidget(dir_button)

        hbox_backup = QHBoxLayout()
        hbox_backup.addWidget(backup_label)
        hbox_backup.addWidget(self.backup_line_edit)
        hbox_backup.addWidget(backup_button)

        ## container for hbox_dir and hbox_backup
        vbox_browse = QVBoxLayout()
        vbox_browse.addLayout(hbox_dir)
        vbox_browse.addLayout(hbox_backup)

        ## container for vbox_browse and analyze button
        hbox_analyze = QHBoxLayout()
        hbox_analyze.addLayout(vbox_browse)
        hbox_analyze.addWidget(analyze_button)
        vbox.addLayout(hbox_analyze)


        # vbox.addStretch()

        self.setLayout(vbox)

        # Set window properties
        self.setWindowTitle('Backup Application')
        self.setGeometry(100, 100, 600, 150)
        self.show()

    def get_directory_to_backup(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory to Backup')
        if directory:
            self.dir_line_edit.setText(directory)

    def get_backup_location(self):
        backup_location = QFileDialog.getExistingDirectory(self, 'Select Backup Location')
        if backup_location:
            self.backup_line_edit.setText(backup_location)

    unique_files_dir = []
    unique_files_backup = []
    unique_folders_dir = []
    unique_folders_backup = []

    def analyze(self):
        directory = self.dir_line_edit.text()
        backup = self.backup_line_edit.text()
        if not (directory and backup):
            return
        
        directory_path = Path(directory)
        backup_path = Path(backup)
        self.compare(directory_path, backup_path)

    def compare(self, path1, path2):
        # Get files in both paths
        files1 = {file.name: file for file in path1.glob('*') if file.is_file()}
        files2 = {file.name: file for file in path2.glob('*') if file.is_file()}

        # Files in path1 but not in path2
        unique_files1 = [files1[file_name] for file_name in files1 if file_name not in files2]
        self.unique_files_dir.append(unique_files1)

        # Files in path2 but not in path1
        unique_files2 = [files2[file_name] for file_name in files2 if file_name not in files1]
        self.unique_files_backup.append(unique_files2)

        # Get folders in both paths
        folders1 = {folder.name: folder for folder in path1.iterdir() if folder.is_dir()}
        folders2 = {folder.name: folder for folder in path2.iterdir() if folder.is_dir()}

        # Folders in path1 but not in path2
        unique_folders1 = [folders1[folder_name] for folder_name in folders1 if folder_name not in folders2]
        self.unique_folders_dir.append(unique_folders1)

        # Folders in path2 but not in path1
        unique_folders2 = [folders2[folder_name] for folder_name in folders2 if folder_name not in folders1]
        self.unique_folders_backup.append(unique_folders2)

        print(files1, '\n', files2, '\n', folders1, '\n', folders2)


def run_app():
    app = QApplication(sys.argv)
    window = BackupApp()
    sys.exit(app.exec_())




if __name__ == '__main__':
    run_app()

