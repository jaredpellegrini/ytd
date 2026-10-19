# YTD - YT Downloader

A simple desktop audio/video downloader app by [Jared Pellegrini](https://github.com/jaredpellegrini)

license [The Unlicense](LICENSE)

I found myself repeatedly copying and pasting the same `yt-dlp` commands any time I wanted to download something. After making a bash script (included in this repo for reference) that made my life *a little bit* easier, I decided to try my hand at creating a Linux desktop app in Python. Enjoy!

## Prerequisite

This application requires **yt-dlp**. You can find more information about it [here](https://github.com/yt-dlp/yt-dlp).

A list of sites supported by `yt-dlp` can be found [here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## Versions

This was originally created Ubuntu 24.04.4 LTS with Python 3.12.3

It now runs on Ubuntu 26.04.1 LTS with Python 3.14.4

## Folders

*These exact locations are not hard requirements, just how I have my environment set up.*
* ytd.py is located in `~/Applications/YTD/`
* The download folder is `~/Downloads/YTD/` (can be changed in the code)

## Running via Terminal

```bash
cd ~/Applications/YTD/
python3 -m venv venv
source venv/bin/activate
python3 ytd.py
```

## Building the app

```bash
cd ~/Applications/YTD/
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install PySide6 pyinstaller
pyinstaller --onefile --name="YTD" ytd.py
# Then execute
./dist/YTD
```

## Desktop file

Create a file in `~/.local/share/applications` called `ytd.desktop` with the following, replacing `user` in the two paths.
```
[Desktop Entry]
Name=YTD
Comment=YT Downloader Application
Exec=/home/user/Applications/YTD/dist/YTD
Icon=/home/user/Applications/YTD/ytd_icon.png
Terminal=false
Type=Application
Categories=Network;Utility;AudioVideo;
```

Then run
```bash
chmod +x ~/.local/share/applications/ytd.desktop
```

## Troubleshooting

After upgrading to Ubuntu 26.04.1, some packages needed to be reinstalled/updated:

```bash
# delete old virtual environment folder
rm -rf venv
# create a new virtual environment w/ new Python version
python3 -m venv venv
# activate it
source venv/bin/activate
# upgrade pip and reinstall dependencies (including PySide6)
pip install --upgrade pip
pip install PySide6
```

`yt-dlp` relies on `ffmpeg` and `ffprobe` to handle tasks like merging video and audio or converting formats

```bash
# update package list and install FFmpeg
sudo apt update
sudo apt install ffmpeg
# verify that both tools are installed correctly
ffmpeg -version
ffprobe -version
```

# CHANGELOG

* v1.0.6: Improved status label, display list number in progress
* v1.0.5: Added progress bar, file size, moved status bar to bottom
* v1.0.4: Consolidated downloads, added format selectors
* v1.0.3: Converted helper to worker
* v1.0.2: Created download helper, improved URL analyzer
* v1.0.1: First version.

# TO DO

* Fix `Trying to disable 0x31a028b0 but 0x0 is focused` message
* Integrate `mp3splt` to split large audio files into separate tracks
* Extract more info from `yt-dlp` output...
    * Progress bar percentage should be out of total number of items when list is detected
    * e.g. \[download\] Downloading item 1 of 4 (each item should account for 25% of progress bar)
