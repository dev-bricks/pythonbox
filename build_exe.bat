@echo off
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PROJECT_ROOT=%CD%"
set "SCANNER=%PROJECT_ROOT%\..\..\_tools\build_exclude_scanner.py"
if not defined BUILD_ROOT set "BUILD_ROOT=%TEMP%\pythonbox_build"
set "EXCLUDES="

for /f "delims=" %%E in ('python "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller') do set "EXCLUDES=%%E"

if not exist "%PROJECT_ROOT%\dist" mkdir "%PROJECT_ROOT%\dist"

python -m PyInstaller ^
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
