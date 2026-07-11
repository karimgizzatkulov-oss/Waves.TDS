@echo off
cd /d "%~dp0"
set "LOG=%~dp0launch.log"
set "PY=%~dp0.venv\Scripts\python.exe"
set "PYW=%~dp0.venv\Scripts\pythonw.exe"

if not exist "%PY%" (
    start notepad "%~dp0launch.bat"
    exit /b 1
)

start "" "%PYW%" calibrate.py
timeout /t 2 /nobreak >nul

tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find /I "pythonw.exe" >nul
if errorlevel 1 (
    "%PY%" calibrate.py >> "%LOG%" 2>&1
    start notepad "%LOG%"
)
