@echo off
cd /d "%~dp0"
set "ROOT=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$root = '%ROOT%';" ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$shell = New-Object -ComObject WScript.Shell;" ^
  "$items = @(" ^
  "  @{ Name = 'TDS Helper'; Target = Join-Path $root 'launch.bat'; Icon = Join-Path $env:SystemRoot 'System32\shell32.dll'; IconIndex = 13 }," ^
  "  @{ Name = 'TDS Calibrate Wave'; Target = Join-Path $root 'launch_calibrate.bat'; Icon = Join-Path $env:SystemRoot 'System32\shell32.dll'; IconIndex = 165 }," ^
  "  @{ Name = 'TDS Calibrate Pump'; Target = Join-Path $root 'launch_calibrate_pump.bat'; Icon = Join-Path $env:SystemRoot 'System32\shell32.dll'; IconIndex = 165 }," ^
  "  @{ Name = 'TDS Setup'; Target = Join-Path $root 'setup.bat'; Icon = Join-Path $env:SystemRoot 'System32\imageres.dll'; IconIndex = 76 }" ^
  ");" ^
  "foreach ($item in $items) {" ^
  "  $path = Join-Path $desktop ($item.Name + '.lnk');" ^
  "  $shortcut = $shell.CreateShortcut($path);" ^
  "  $shortcut.TargetPath = $item.Target;" ^
  "  $shortcut.WorkingDirectory = $root;" ^
  "  $shortcut.IconLocation = ($item.Icon + ',' + $item.IconIndex);" ^
  "  $shortcut.Description = $item.Name;" ^
  "  $shortcut.Save();" ^
  "  Write-Host ('Created: ' + $path)" ^
  "}"

echo.
echo Desktop shortcuts created.
if /I not "%~1"=="nopause" pause
