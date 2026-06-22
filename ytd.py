"""
Module Name: ytd.py
Description: A simple desktop audio/video downloader app
Author: jpellegrini
Date: 2026-06-22
Version: 1.0.4
License: The Unlicense
"""

import os
import sys
from PySide6.QtCore import (QProcess, Qt, QUrl)
from PySide6.QtGui import (QDesktopServices, QIcon)
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
                               QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
from downloader import DownloaderWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version_number = "1.0.4"

        # Add hover color to all app buttons
        app.setStyleSheet("QPushButton:hover { background-color: #ccccff; }")

        # Set download path, create if it doesn't exits, ignore if it does
        self.target_path = os.path.expanduser("~/Downloads/YTD")
        os.makedirs(self.target_path, exist_ok=True)

        # Instantiate the worker
        self.worker = DownloaderWorker()
        # Connect the worker signals to UI functions
        self.worker.output_received.connect(self.update_console_with_process_output)
        self.worker.finished.connect(self.on_process_finished)

        self.build_ui()

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
        instructions_label = QLabel('\n<a href="https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md">Supported Sites</a>\n')
        instructions_label.setOpenExternalLinks(True)
        top_layout.addWidget(instructions_label)

        # Add button to open the download folder
        button_open_folder = QPushButton("Open Downloads folder")
        button_open_folder.clicked.connect(self.open_folder)
        button_open_folder.setStyleSheet("QPushButton { min-width: 200px; max-width: 200px; padding: 5px; }")
        top_layout.addWidget(button_open_folder)

        layout.addWidget(top_row)

        # Add the url text box
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter a URL")
        self.url_input.textChanged.connect(self.validate_inputs)
        url_action = self.url_input.addAction(QIcon.fromTheme("edit-clear"), QLineEdit.TrailingPosition)
        url_action.triggered.connect(self.url_input.clear)
        layout.addWidget(self.url_input)

        # Add optional tracknumbers box
        self.tracknumbers_row = QWidget()
        self.tracknumbers_row.setFixedWidth(475)
        tracknumbers_layout = QHBoxLayout(self.tracknumbers_row)
        tracknumbers_layout.setContentsMargins(0, 0, 0, 0)
        tracknumbers_label = QLabel("Optional: Specify track numbers (e.g. '1:3,7')")
        tracknumbers_layout.addWidget(tracknumbers_label)
        self.tracknumbers_input = QLineEdit()
        self.tracknumbers_input.setFixedWidth(150)
        tracknumbers_action = self.tracknumbers_input.addAction(QIcon.fromTheme("edit-clear"), QLineEdit.TrailingPosition)
        tracknumbers_action.triggered.connect(self.tracknumbers_input.clear)
        tracknumbers_layout.addWidget(self.tracknumbers_input)
        layout.addWidget(self.tracknumbers_row)
        self.tracknumbers_row.hide()

        # Add format options
        self.formats_row = QWidget()
        # self.formats_row.setFixedWidth(400)
        formats_layout = QHBoxLayout(self.formats_row)
        formats_layout.setContentsMargins(0, 0, 0, 0)
        formats_label = QLabel("Formats: ")
        formats_layout.addWidget(formats_label)
        self.format_mp3_cbx = QCheckBox("MP3 audio", self)
        self.format_mp3_cbx.checkStateChanged.connect(self.validate_inputs)
        formats_layout.addWidget(self.format_mp3_cbx)
        self.format_mp4_cbx = QCheckBox("MP4 video", self)
        self.format_mp4_cbx.checkStateChanged.connect(self.validate_inputs)
        formats_layout.addWidget(self.format_mp4_cbx)
        self.format_srt_cbx = QCheckBox("SRT subtitles", self)
        self.format_srt_cbx.checkStateChanged.connect(self.validate_inputs)
        formats_layout.addWidget(self.format_srt_cbx)

        # Add the download button
        self.button_download = QPushButton("Start Download")
        self.button_download.setStyleSheet("QPushButton { min-width: 200px; max-width: 200px; padding: 5px; font-weight:bold; margin-left: 200px; }")
        self.button_download.clicked.connect(self.download_files)
        self.button_download.setEnabled(False)
        formats_layout.addWidget(self.button_download)

        layout.addWidget(self.formats_row)

        # Add a status label
        self.status_label = QLabel("\n")
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
   
    def validate_inputs(self):
        self.url_results = DownloaderWorker.analyze_url(self.url_input.text())

        if not self.url_results["is_valid"]:
            self.tracknumbers_row.hide()
            self.button_download.setEnabled(False)
        else:
            # if link contains both a YT video ID and a playlist ID, prompt to choose
            if self.url_results["list_id"] is not None and self.url_results["video_id"] is not None:
                self.prompt_single_or_playlist()

            if self.url_results["list_id"] is not None:
                self.tracknumbers_row.show()
            else:
                self.tracknumbers_row.hide()

            if not self.format_mp3_cbx.isChecked() and not self.format_mp4_cbx.isChecked() and not self.format_srt_cbx.isChecked():
                self.button_download.setEnabled(False)
            else:
                self.button_download.setEnabled(True)

    def prompt_single_or_playlist(self):
        msg = QMessageBox()
        msg.setWindowTitle("Playlist Video Link")
        msg.setText("This link contains both a video and a playlist.")
        msg.setInformativeText("Do you want to download just the video or the whole playlist?")
        btn_video = msg.addButton("Video", QMessageBox.ActionRole)
        btn_video.setStyleSheet("QPushButton { min-width: 120px; max-width: 120px; padding: 5px; margin-right: 25px; }")
        btn_playlist = msg.addButton("Playlist", QMessageBox.ActionRole)
        btn_playlist.setStyleSheet("QPushButton { min-width: 120px; max-width: 120px; padding: 5px; margin-right: 25px; }")
        btn_cancel = msg.addButton("Cancel", QMessageBox.ActionRole)
        btn_cancel.setStyleSheet("QPushButton { min-width: 120px; max-width: 120px; padding: 5px; }")
        msg.exec()

        self.url_input.blockSignals(True)  # Stop the signal from firing
        if msg.clickedButton() == btn_video:
            self.url_input.setText(DownloaderWorker.reconstruct_url(self.url_input.text(), "v"))
            self.url_results["list_id"] = None
        elif msg.clickedButton() == btn_playlist:
            self.url_input.setText(DownloaderWorker.reconstruct_url(self.url_input.text(), "list"))
            self.url_results["video_id"] = None
        elif msg.clickedButton() == btn_cancel:
            self.url_input.setText("")
            self.url_results["video_id"] = None
            self.url_results["list_id"] = None
        self.url_input.blockSignals(False) # Turn the signal back on

    def download_files(self):
        self.button_download.setEnabled(False)
        self.status_label.setText(f"\nDownloading...")
        self.output_label.setText("Starting download...\n")
        self.status_label.setStyleSheet("color: black;")
        if self.format_mp3_cbx.isChecked():
            self.worker.download_files(
                self.url_input.text(),
                self.target_path,
                "mp3",
                bool(self.url_results["list_id"] is not None),
                self.tracknumbers_input.text()
            )
        if self.format_mp4_cbx.isChecked():
            self.worker.download_files(
                self.url_input.text(),
                self.target_path,
                "mp4",
                bool(self.url_results["list_id"] is not None),
                self.tracknumbers_input.text()
            )
        if self.format_srt_cbx.isChecked():
            self.worker.download_subtitles(
                self.url_input.text(),
                self.target_path,
                bool(self.url_results["list_id"] is not None),
                self.tracknumbers_input.text()
            )

    def update_console_with_process_output(self, data: str):
        # Append the new data to the label's existing text
        current_text = self.output_label.text()
        self.output_label.setText(current_text + data)
        
        # Auto-scroll to the bottom
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_process_finished(self, _command, exit_code, num_remaining_processes):
        if exit_code == 0 and num_remaining_processes == 0:
            self.status_label.setStyleSheet("color: green;")
            self.status_label.setText("\nSuccess!")
        elif self.worker.process.exitStatus() == QProcess.Crashed:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"\nError: Process crashed!")
        elif exit_code != 0:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"\nError: Process exited with code {exit_code}")
            
        # When the queue is empty, re-validate inputs to enable new download
        if num_remaining_processes == 0:
            self.validate_inputs()

    def open_folder(self):
        # already confirmed above that the folder exists, but check again just in case
        if os.path.exists(self.target_path):
            url = QUrl.fromLocalFile(self.target_path)
            QDesktopServices.openUrl(url)
        else:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"\nPath not found: {self.target_path}")

if __name__ == '__main__':
    # Run the app
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

