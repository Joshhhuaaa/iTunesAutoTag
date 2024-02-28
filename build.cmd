@echo off
py -m PyInstaller --onefile iTunesAutoTag.py --icon=icon.ico
pyi-set_version "version-info" "dist\iTunesAutoTag.exe"
