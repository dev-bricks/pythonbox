@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo        PythonBox v8 starten
echo ========================================
echo.

if exist "dist\PythonBox.exe" (
    echo Starte dist\PythonBox.exe...
    start "" "dist\PythonBox.exe" %*
    exit /b 0
)

if exist "PythonBox.exe" (
    echo Starte PythonBox.exe...
    start "" "PythonBox.exe" %*
    exit /b 0
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Keine EXE und Python nicht gefunden!
    echo Bitte Python 3.10+ installieren oder build_exe.bat ausführen.
    echo.
    pause
    exit /b 1
)

echo Keine EXE gefunden, starte Python-Fallback...
echo.
python PythonBox_v8.py %*

if errorlevel 1 (
    echo.
    echo [FEHLER] Anwendung mit Fehler beendet.
    pause
)
