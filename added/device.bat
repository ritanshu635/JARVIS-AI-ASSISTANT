@echo off
echo Checking ADB connection...
adb devices
if %errorlevel% neq 0 (
    echo ADB not found or no devices connected
    echo Please ensure:
    echo 1. Android device is connected via USB
    echo 2. USB debugging is enabled
    echo 3. ADB is installed and in PATH
) else (
    echo ADB connection ready
)
pause