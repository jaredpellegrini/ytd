"""
Module Name: ytd.py
Description: A simple desktop audio/video downloader app
Author: jpellegrini
Date: 2026-06-14
Version: 1.0.1
License: The Unlicense
"""

import os
import sys
from PySide6.QtCore import (QProcess, Qt, QUrl)
from PySide6.QtGui import (QDesktopServices, QIcon)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLineEdit, QLabel, QScrollArea, QSpacerItem, QSizePolicy)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version_number = "1.0.1"

        app.setStyleSheet("""
            QPushButton {
                min-width: 350px;
                max-width: 350px;
            }
            QPushButton:hover {
                background-color: #ccccff;
            }
        """)

        self.build_ui()

        # Set download path, create if it doesn't exits, ignore if it does
        self.target_path = os.path.expanduser("~/Downloads/YTD")
        os.makedirs(self.target_path, exist_ok=True)

        # Initialize the d/l process
        self.process = QProcess()
        # Connect the output signal to the update function
        self.process.readyReadStandardOutput.connect(self.update_console_with_process_output)
        # Run when the process finishes
        self.process.finished.connect(self.on_process_finished)

    def build_ui(self):
        self.setWindowTitle("YT Downloader")
        self.resize(800, 600)

         # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        top_row = QWidget()
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Add some instructions
        instructions_label = QLabel("URL formats:\n\nhttps://www.youtube.com/watch?v=... (single video)\nhttps://www.youtube.com/playlist?list=... (playlist)\n")
        top_layout.addWidget(instructions_label)

        # Add button to open the download folder
        button_open_folder = QPushButton("Open Downloads folder")
        button_open_folder.clicked.connect(self.open_folder)
        button_open_folder.setStyleSheet("""QPushButton { min-width: 200px; max-width: 200px; padding: 5px; margin-right: 25px; } """)
        top_layout.addWidget(button_open_folder)

        layout.addWidget(top_row)

        # Add the url text box
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter a URL")
        self.url_input.textChanged.connect(self.validate_url)
        url_action = self.url_input.addAction(QIcon.fromTheme("edit-clear"), QLineEdit.TrailingPosition)
        url_action.triggered.connect(self.url_input.clear)
        layout.addWidget(self.url_input)

        # Add optional tracknumbers box
        self.tracknumbers_row = QWidget()
        self.tracknumbers_row.setFixedWidth(475)
        tracknumbers_layout = QHBoxLayout(self.tracknumbers_row)
        tracknumbers_layout.setContentsMargins(0, 0, 0, 0)
        tracknumbers_label = QLabel("Optional: Specify track numbers (e.g. \"1:3,7\")")
        tracknumbers_layout.addWidget(tracknumbers_label)
        self.tracknumbers_input = QLineEdit()
        self.tracknumbers_input.setFixedWidth(150)
        tracknumbers_action = self.tracknumbers_input.addAction(QIcon.fromTheme("edit-clear"), QLineEdit.TrailingPosition)
        tracknumbers_action.triggered.connect(self.tracknumbers_input.clear)
        tracknumbers_layout.addWidget(self.tracknumbers_input)
        layout.addWidget(self.tracknumbers_row)
        self.tracknumbers_row.hide()

        # Add the download buttons
        buttons_row1 = QWidget()
        buttons_layout1 = QHBoxLayout(buttons_row1)
        buttons_layout1.setContentsMargins(0, 0, 0, 0)

        self.button_playlist = QPushButton("Download a playlist as mp3 audio")
        self.button_playlist.clicked.connect(self.download_playlist)
        self.button_playlist.setEnabled(False)
        buttons_layout1.addWidget(self.button_playlist)

        self.button_single_mp4 = QPushButton("Download a single video as mp4 file")
        self.button_single_mp4.clicked.connect(lambda: self.download_single_file("mp4"))
        self.button_single_mp4.setEnabled(False)
        buttons_layout1.addWidget(self.button_single_mp4)

        layout.addWidget(buttons_row1)

        buttons_row2 = QWidget()
        buttons_layout2 = QHBoxLayout(buttons_row2)
        buttons_layout2.setContentsMargins(0, 0, 0, 0) # Removes default padding

        self.button_single_mp3 = QPushButton("Download a single video as mp3 audio")
        self.button_single_mp3.clicked.connect(lambda: self.download_single_file("mp3"))
        self.button_single_mp3.setEnabled(False)
        buttons_layout2.addWidget(self.button_single_mp3)

        self.button_subtitles = QPushButton("Download subtitles to srt file")
        self.button_subtitles.clicked.connect(self.download_subtitles)
        self.button_subtitles.setEnabled(False)
        buttons_layout2.addWidget(self.button_subtitles)

        layout.addWidget(buttons_row2)

        # Add a status label
        self.status_label = QLabel(f"\n")
        layout.addWidget(self.status_label)

        # Create a Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # Important: allows label to fill the area
        self.scroll_area.setStyleSheet("background-color: black; border: 1px solid #333;")
        self.output_label = QLabel("")
        self.output_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.output_label.setStyleSheet("color: white; font-family: 'Courier New', Courier, monospace; font-size: 12px; padding: 5px;")
        self.scroll_area.setWidget(self.output_label)
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.scroll_area)
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Create the version label
        version_label = QLabel(f"v{self.version_number}")
        version_label.setStyleSheet("color: #666666; font-size: 12px;")
        version_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        layout.addWidget(version_label)
   
    def validate_url(self):
        prefix_playlist = "https://www.youtube.com/playlist"
        prefix_single = "https://www.youtube.com/watch"
        is_playlist = self.url_input.text().startswith(prefix_playlist)
        is_single = self.url_input.text().startswith(prefix_single)
        self.button_playlist.setEnabled(is_playlist)
        self.button_single_mp3.setEnabled(is_single)
        self.button_single_mp4.setEnabled(is_single)
        self.button_subtitles.setEnabled(is_single)
        if is_playlist:
            self.tracknumbers_row.show()
        else:
            self.tracknumbers_row.hide()

    def disable_buttons(self):
        self.button_playlist.setEnabled(False)
        self.button_single_mp3.setEnabled(False)
        self.button_single_mp4.setEnabled(False)
        self.button_subtitles.setEnabled(False)

    def download_playlist(self):
        self.disable_buttons()
        self.status_label.setStyleSheet("color: black;")
        self.status_label.setText("\nDownloading playlist...")
        url = self.url_input.text()
        tracknumbers = self.tracknumbers_input.text()
        command = [
            "yt-dlp", 
            "-t", "mp3",
            "--output", f"{self.target_path}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
        ]
        if tracknumbers:
            command.extend(["--playlist-items", tracknumbers])
        command.extend([url])
        self.process.start(command[0], command[1:])
        self.output_label.setText("Starting download...\n")

    def download_single_file(self, format):
        self.disable_buttons()
        self.status_label.setStyleSheet("color: black;")
        self.status_label.setText(f"\nDownloading {format}...")
        url = self.url_input.text()
        command = [
            "yt-dlp", 
            "-t", format,
            "--output", f"{self.target_path}/%(title)s.%(ext)s",
            url
        ]
        self.process.start(command[0], command[1:])
        self.output_label.setText("Starting download...\n")

    def download_subtitles(self):
        self.disable_buttons()
        self.status_label.setStyleSheet("color: black;")
        self.status_label.setText("\nDownloading subtitles...")
        url = self.url_input.text()
        command = [
            "yt-dlp", 
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--sub-format", "srt",   
            "--output", f"{self.target_path}/%(title)s.%(ext)s",
            url
        ]
        self.process.start(command[0], command[1:])
        self.output_label.setText("Starting download...\n")

    def update_console_with_process_output(self):
        # Read the data from the process
        data = self.process.readAllStandardOutput().data().decode()
        
        # Append the new data to the label's existing text
        current_text = self.output_label.text()
        self.output_label.setText(current_text + data)
        
        # Auto-scroll to the bottom
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_process_finished(self, exit_code, exit_status):
        if exit_code == 0:
            self.status_label.setStyleSheet("color: green;")
            self.status_label.setText("\nSuccess!")
        else:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"\nError: Process exited with code {exit_code}")
            
        # Re-enable appropriate buttons
        self.validate_url()

    def open_folder(self):
        # already confirmed above that the folder exists, but check again just in case
        if os.path.exists(self.target_path):
            url = QUrl.fromLocalFile(self.target_path)
            QDesktopServices.openUrl(url)
        else:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"\nPath not found: {self.target_path}")


# Run the app
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
