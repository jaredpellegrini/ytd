import re
from PySide6.QtCore import QObject, Signal, QProcess
from urllib.parse import urlparse

class DownloaderWorker(QObject):
    output_received = Signal(str)
    finished = Signal(int, QProcess.ExitStatus)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.process = QProcess()
        # Wire up the process signals to the internal handlers
        self.process.readyReadStandardOutput.connect(self._handle_output)
        self.process.finished.connect(self.finished)
        self.process.errorOccurred.connect(self._handle_error)

    def _handle_output(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output_received.emit(data)

    def _handle_error(self, error):
        self.error.emit(f"Process error: {error}")

    @staticmethod
    def analyze_url(url: str) -> dict:
        results = {"is_valid": False, "is_video": False, "is_playlist": False}
        parsed = urlparse(url)
        # First check if the string is a valid URL at all
        if all([parsed.scheme, parsed.netloc]):
            results["is_valid"] = True
            # Check if the string is for a YouTube video by looking for the 11-character video ID
            video_pattern = r"(?:v=|/v/|/embed/|/shorts/|youtu\.be/)([a-zA-Z0-9_-]{11})"
            if re.search(video_pattern, url):
                results["is_video"] = True
            # Check if the string is a playlist by looking for "list=" in the query string
            if "list=" in parsed.query:
                results["is_playlist"] = True
        return results

    def run_command(self, command: list):
        if self.process.state() == QProcess.Running:
            self.output_received.emit("Error: A process is already running.\n")
            return
        self.process.start(command[0], command[1:])

    def download_playlist(self, url: str, path: str, format: str, tracknumbers: str):
        cmd = [
            "yt-dlp", 
            "-t", format,
            "--output", f"{path}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
        ]
        if tracknumbers:
            cmd.extend(["--playlist-items", tracknumbers])
        cmd.extend([url])
        self.run_command(cmd)

    def download_single_file(self, url: str, path: str, format: str):
        cmd = [
            "yt-dlp", 
            "-t", format,
            "--output", f"{path}/%(title)s.%(ext)s",
            url
        ]
        self.run_command(cmd)

    def download_subtitles(self, url: str, path: str):
        cmd = [
            "yt-dlp", 
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--sub-format", "srt",   
            "--output", f"{path}/%(title)s.%(ext)s",
            url
        ]
        self.run_command(cmd)
