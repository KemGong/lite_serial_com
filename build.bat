@echo off
echo Checking Python version...
python --version

echo Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /f /q *.spec 2>nul

echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller
python -m pip install --upgrade pyserial

echo Generating spec file...
python -m PyInstaller --name SerialDebugger ^
    --onefile ^
    --windowed ^
    --add-data "icon.ico;." ^
    --hidden-import serial.tools.list_ports ^
    --hidden-import serial.tools.list_ports_common ^
    serial_debugger.py

echo Building executable...
python -m PyInstaller --clean --noconfirm SerialDebugger.spec

echo Build complete!
echo The executable is in the dist folder.
pause 