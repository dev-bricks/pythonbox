@echo off
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PROJECT_ROOT=%CD%"
set "SCANNER=%PROJECT_ROOT%\..\..\_tools\build_exclude_scanner.py"
if not defined BUILD_ROOT set "BUILD_ROOT=C:\_Local_DEV\codex_build\pythonbox"
if not defined BUILD_VENV set "BUILD_VENV=C:\_Local_DEV\venvs\pythonbox_build"
set "BUILD_PYTHON=%BUILD_VENV%\Scripts\python.exe"
set "EXCLUDE_ARGS=%BUILD_ROOT%\pyinstaller_excludes.txt"
set "EXCLUDES="

if not exist "%BUILD_PYTHON%" (
    python -m venv "%BUILD_VENV%"
    if errorlevel 1 exit /b 1
)

"%BUILD_PYTHON%" -m pip install -r "%PROJECT_ROOT%\requirements.txt" pyinstaller
if errorlevel 1 (
    echo.
    echo [FEHLER] Build-Abhängigkeiten konnten nicht installiert werden.
    exit /b 1
)

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"
"%BUILD_PYTHON%" "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller > "%EXCLUDE_ARGS%"
if errorlevel 1 (
    echo.
    echo [FEHLER] Build-Exclude-Scanner fehlgeschlagen.
    exit /b 1
)
set /p EXCLUDES=<"%EXCLUDE_ARGS%"

if not exist "%PROJECT_ROOT%\dist" mkdir "%PROJECT_ROOT%\dist"

"%BUILD_PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name PythonBox ^
  --icon "%PROJECT_ROOT%\PythonBox.ico" ^
  --add-data "%PROJECT_ROOT%\locales;locales" ^
  %EXCLUDES% ^
  --distpath "%BUILD_ROOT%\dist" ^
  --workpath "%BUILD_ROOT%\build" ^
  --specpath "%BUILD_ROOT%" ^
  "%PROJECT_ROOT%\PythonBox_v8.py"

if errorlevel 1 (
    echo.
    echo [FEHLER] PyInstaller-Build fehlgeschlagen.
    exit /b 1
)

copy /Y "%BUILD_ROOT%\dist\PythonBox.exe" "%PROJECT_ROOT%\dist\PythonBox.exe" >nul
copy /Y "%BUILD_ROOT%\dist\PythonBox.exe" "%PROJECT_ROOT%\PythonBox.exe" >nul

echo.
echo [OK] EXE aktualisiert:
echo   %PROJECT_ROOT%\dist\PythonBox.exe
echo   %PROJECT_ROOT%\PythonBox.exe
