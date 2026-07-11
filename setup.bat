@echo off
cd /d "%~dp0"
echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo Failed to create venv.
    pause
    exit /b 1
)

echo Installing dependencies (may take a few minutes)...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo Install failed.
    pause
    exit /b 1
)

echo.
echo Creating desktop shortcuts...
call "%~dp0create_desktop_shortcuts.bat" nopause

echo.
echo Done! You can now use the desktop shortcuts.
pause
