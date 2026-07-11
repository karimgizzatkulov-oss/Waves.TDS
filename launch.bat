@echo off
cd /d "%~dp0"
set "LOG=%~dp0launch.log"
set "PY=%~dp0.venv\Scripts\python.exe"
set "PYW=%~dp0.venv\Scripts\pythonw.exe"

if not exist "%PY%" (
    echo [%date% %time%] Virtual env not found. Run setup first.>> "%LOG%"
    echo Virtual environment not found.>> "%TEMP%\tds-helper-error.txt"
    echo Run in terminal:>> "%TEMP%\tds-helper-error.txt"
    echo   cd "%~dp0">> "%TEMP%\tds-helper-error.txt"
    echo   python -m venv .venv>> "%TEMP%\tds-helper-error.txt"
    echo   .venv\Scripts\pip install -r requirements.txt>> "%TEMP%\tds-helper-error.txt"
    start notepad "%TEMP%\tds-helper-error.txt"
    exit /b 1
)

"%PY%" -c "import mss, easyocr, cv2" 2>> "%LOG%"
if errorlevel 1 (
    echo [%date% %time%] Missing packages.>> "%LOG%"
    echo Installing dependencies...>> "%LOG%"
    "%PY%" -m pip install -r requirements.txt >> "%LOG%" 2>&1
)

start "" "%PYW%" main.py
timeout /t 2 /nobreak >nul

tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find /I "pythonw.exe" >nul
if errorlevel 1 (
    echo [%date% %time%] App failed to start.>> "%LOG%"
    "%PY%" main.py >> "%LOG%" 2>&1
    echo Startup failed. See:>> "%TEMP%\tds-helper-error.txt"
    type "%LOG%" >> "%TEMP%\tds-helper-error.txt"
    start notepad "%TEMP%\tds-helper-error.txt"
)
