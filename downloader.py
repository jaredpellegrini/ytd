import re
from PySide6.QtCore import QObject
from urllib.parse import urlparse

class DownloaderHelper(QObject):
    def analyze_url(url: str) -> dict:
        results = {"is_valid": False, "is_video": False, "is_playlist": False}

        # Check if the string is a valid URL at all
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return results
        results["is_valid"] = True
        
        # Check if the string is for a YouTube video by looking for the 11-character video ID
        video_pattern = r"(?:v=|/v/|/embed/|/shorts/|youtu\.be/)([a-zA-Z0-9_-]{11})"
        if re.search(video_pattern, url):
            results["is_video"] = True
            
        # Check if the string is a playlist by looking for "list=" in the query string
        if "list=" in parsed.query:
            results["is_playlist"] = True
            
        return results

    def download_playlist(self, url: str, path: str, format: str, tracknumbers: str):
        command = [
            "yt-dlp", 
            "-t", format,
            "--output", f"{path}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"
        ]
        if tracknumbers:
            command.extend(["--playlist-items", tracknumbers])
        command.extend([url])
        self.process.start(command[0], command[1:])

    def download_single_file(self, url: str, path: str, format: str):
        command = [
            "yt-dlp", 
            "-t", format,
            "--output", f"{path}/%(title)s.%(ext)s",
            url
        ]
        self.process.start(command[0], command[1:])

    def download_subtitles(self, url: str, path: str):
        command = [
            "yt-dlp", 
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--sub-format", "srt",   
            "--output", f"{path}/%(title)s.%(ext)s",
            url
        ]
        self.process.start(command[0], command[1:])
