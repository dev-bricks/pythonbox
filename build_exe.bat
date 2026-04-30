@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name PythonBox ^
  --icon "PythonBox.ico" ^
  --add-data "locales;locales" ^
  PythonBox_v8.py
