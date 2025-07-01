@echo off
REM Build ebook_reader for Windows
REM Usage: build_win.bat

REM Ensure we are in the script's directory
cd /d %~dp0

REM Install required packages
pip install --upgrade pip
pip install pyinstaller pymupdf ebooklib

REM Build the app using the .spec file for correct hidden imports and data
pyinstaller ebook_reader.spec

if exist dist\ebook_reader.exe (
    echo Build complete! Find your executable in the dist\ folder.
) else (
    echo Build failed. Please check the output above for errors.
)
pause
