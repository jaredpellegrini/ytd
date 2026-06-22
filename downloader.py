import re
from PySide6.QtCore import QObject, Signal, QProcess
from urllib.parse import urlparse, parse_qs

class DownloaderWorker(QObject):
    output_received = Signal(str)
    finished = Signal(list, int, int)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.process = QProcess()
        self.queue = []
        self.current_command = None

        # Wire up the process signals to the internal handlers
        self.process.readyReadStandardOutput.connect(self._handle_output)
        self.process.finished.connect(self._on_process_finished)
        self.process.errorOccurred.connect(self._handle_error)

    def add_to_queue(self, command):
        self.queue.append(command)
        if self.process.state() == QProcess.NotRunning:
            self._process_next()

    def _process_next(self, *args):
        if self.queue:
            self.current_command = self.queue.pop(0)
            self.process.start(self.current_command[0], self.current_command[1:])

    def _on_process_finished(self, exit_code, exit_status):
        # Signal that this process finished
        if self.current_command:
            self.finished.emit(self.current_command, exit_code, len(self.queue))
        # Trigger the next item in the queue
        self._process_next()

    def _handle_output(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output_received.emit(data)

    def _handle_error(self, error):
        self.error.emit(f"Process error: {error}")

    def download_files(self, url: str, path: str, format: str, is_playlist: bool, tracknumbers: str):
        cmd = [
            "yt-dlp", 
            "-t", format
        ]
        if is_playlist:
            cmd.extend(["--output", f"{path}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"])
            if tracknumbers:
                cmd.extend(["--playlist-items", tracknumbers])
        else:
            cmd.extend(["--output", f"{path}/%(title)s.%(ext)s"])
        cmd.extend([url])
        self.add_to_queue(cmd)

    def download_subtitles(self, url: str, path: str, is_playlist: bool, tracknumbers: str):
        cmd = [
            "yt-dlp", 
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--sub-format", "srt"
        ]
        if is_playlist:
            cmd.extend(["--output", f"{path}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"])
            if tracknumbers:
                cmd.extend(["--playlist-items", tracknumbers])
        else:
            cmd.extend(["--output", f"{path}/%(title)s.%(ext)s"])
        cmd.extend([url])
        self.add_to_queue(cmd)

    @staticmethod
    def analyze_url(url: str) -> dict:
        results = {"is_valid": False, "video_id": None, "list_id": None}
        parsed = urlparse(url)
        # First check if the string is a valid URL at all
        if all([parsed.scheme, parsed.netloc]):
            results["is_valid"] = True
            params = parse_qs(parsed.query)
            results["video_id"] = params.get("v", [None])[0]
            results["list_id"] = params.get("list", [None])[0]
        return results

    @staticmethod
    def reconstruct_url(url, key):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        new_url = parsed.scheme + "://" + parsed.netloc
        if key == "v":
            new_url += "/watch?v=" + params.get("v", [None])[0]
        elif key == "list":
            new_url += "/playlist?list=" + params.get("list", [None])[0]
        return new_url
