# Smart Backup

Smart Backup is a Python-based desktop application that helps you easily manage and synchronize files and folders between a source directory and a backup location. It provides a user-friendly graphical interface (GUI) that allows you to analyze the differences between the two directories and selectively decide which files and folders to keep, copy, or remove.

I created this application to manage a shared backup between my desktop and laptop. Because I'm a supporter of digital minimalism, I wanted to build an application that helps me keep my directories as tidy as possible and speed up the backup process.

## Features

- **Directory Comparison**: Compare the contents of a source directory with a backup location, identifying files and folders that are unique to each directory or have different modification dates.
- **User-friendly Interface**: Intuitive GUI with tables and checkboxes to select which files and folders to keep, copy, or remove. Hover on icons for a description of what the corresponding checkboxes accomplish.
- **Folder Handling**: Copy or remove entire folders (including their contents) from the source or backup location.
- **File Handling**: Keep, copy, or remove individual files between the source and backup directories.
- **Different Modification Dates**: Handle files that have different modification dates in the source and backup directories, with options to keep both versions (renaming them with the modification date) or choose just one version.
- **Default Behavior Reflecting Common Needs**: For each file or folder to handle, checkboxes are already set to reflect common user needs. By default, files and folders only present in the source directory will be copied to the backup directory; files and folders only present in the backup directory will only be kept there; for files that have different dates modified, the most recent version will be copied in both source and backup directory.
- **Progress Tracking**: Monitor the backup process with a progress bar.

## Installation

1. Download the `backup.py` script.
2. Install the required dependencies by running `pip install PyQt5`.
3. Run the `backup.py` script to launch the Smart Backup application.

## Usage

1. Select the source directory you want to back up and the backup location using the "Browse" buttons.
2. Click the "Analyze" button to compare the two directories.
3. The application will display tables with the following information:
   - Folders and files that are unique to the source directory
   - Folders and files that are unique to the backup location
   - Files that have different modification dates in the source and backup directories
4. Use the checkboxes in the tables to select the desired action for each item (keep in source, copy to backup, keep in backup, copy to source).
5. Click the "Backup" button to perform the selected actions.
6. Monitor the progress bar to track the backup process.

## Dependencies

- Python 3.x
- PyQt5