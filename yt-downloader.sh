#!/bin/bash

# Enable case-insensitive matching
shopt -s nocasematch

cd ./Downloads/yt-dlp/

download_single_file() {
    yt-dlp -t "$1" --output "%(title)s.%(ext)s" "$2"
}

download_subtitles() {
    yt-dlp --skip-download --write-subs --write-auto-subs --sub-lang en --sub-format srt --output "%(title)s.%(ext)s" "$1"
}

while true; do
    echo -e "\e[32m\n--- YT DOWNLOADER (x to quit) ---\e[0m"
    echo "1) Download a single video as mp3 audio"
    echo "2) Download a playlist as mp3 audio"
    echo "3) Download a single video as mp4 file"
    echo "4) Download subtitles to srt file"
    read -p "Select [1-4]: " choice

    case $choice in
        1)
            echo -e "\nEnter a URL like \"https://www.youtube.com/watch?v=...\"" 
            echo "or enter \"x\" to go back" 
            read -p "URL: " url
            if [[ "$url" == https://www.youtube.com/watch* ]]; then
                download_single_file "mp3" "$url"
            elif [[ "$url" != x ]]; then
                echo -e "\e[31mInvalid URL. Try again.\e[0m"
            fi
            ;;
            
        2)
            echo -e "\nEnter a URL like \"https://www.youtube.com/playlist?list=...\"" 
            echo "or enter \"x\" to go back" 
            read -p "URL: " url
            if [[ "$url" == https://www.youtube.com/playlist* ]]; then
                read -p "Specify track numbers (e.g. \"1:20\") or hit Enter to download all: " tracknumbers
                if [[ -z "$tracknumbers" ]]; then
                    yt-dlp -t mp3 --output "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "$url"
                else
                    yt-dlp -t mp3 -I "$tracknumbers" --output "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "$url"
                fi
            elif [[ "$url" != x ]]; then
                echo -e "\e[31mInvalid URL. Try again.\e[0m"
            fi
            ;;

        3)
            echo -e "\nEnter a URL like \"https://www.youtube.com/watch?v=...\"" 
            echo "or enter \"x\" to go back" 
            read -p "URL: " url
            if [[ "$url" == https://www.youtube.com/watch* ]]; then
                download_single_file "mp4" "$url"
                read -p "Enter Y to download subtitles: " subtitles
                if [[ "$subtitles" == y ]]; then
                    download_subtitles "$url"
                fi
            elif [[ "$url" != x ]]; then
                echo -e "\e[31mInvalid URL. Try again.\e[0m"
            fi
            ;;

        4)
            echo -e "\nEnter a URL like \"https://www.youtube.com/watch?v=...\"" 
            echo "or enter \"x\" to go back" 
            read -p "URL: " url
            if [[ "$url" == https://www.youtube.com/watch* ]]; then
                download_subtitles "$url"
            elif [[ "$url" != x ]]; then
                echo -e "\e[31mInvalid URL. Try again.\e[0m"
            fi
            ;;

        x) echo ""; break ;;
        *) echo -e "\e[31mInvalid choice. Try again.\e[0m" ;;
    esac
done

