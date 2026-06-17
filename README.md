# YTD - YT Downloader

A simple desktop audio/video downloader app by [Jared Pellegrini](https://github.com/jaredpellegrini)

license [The Unlicense](LICENSE)

I found myself repeatedly copying and pasting the same `yt-dlp` commands any time I wanted to download something. After making a bash script (included in this repo for reference) that made my life *a little bit* easier, I decided to try my hand at creating a Linux desktop app in Python. Enjoy!

## Prerequisite

This application requires that **yt-dlp** is installed. You can find more information about it [here](https://github.com/yt-dlp/yt-dlp).

## Versions

This was created and runs on Ubuntu 24.04.4 LTS with Python 3.12.3

## Folders

*These exact locations are not hard requirements, just how I have my environment set up.*
* app.py is located in `~/Applications/YTD/`
* The download folder is `~/Downloads/YTD/` (can be changed in the code)

## Running via Terminal

```bash
cd ~/Applications/YTD/
python3 -m venv venv
source venv/bin/activate
python3 app.py
```

## Building the app

```bash
cd ~/Applications/YTD/
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install PySide6 pyinstaller
pyinstaller --onefile --name="YTD" app.py
# Then execute
./dist/YTD
```

## Desktop file in ~/.local/share/applications

```bash
chmod +x ~/.local/share/applications/ytd.desktop
```

# CHANGELOG

* v1.0.1: First version.
