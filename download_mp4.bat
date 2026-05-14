@echo off

if "%~1"=="" (
    echo Usage:
    echo download_mp4.bat "VIDEO_URL"
    pause
    exit /b
)

yt-dlp -f "bv*+ba/b" --merge-output-format mp4 %1

pause