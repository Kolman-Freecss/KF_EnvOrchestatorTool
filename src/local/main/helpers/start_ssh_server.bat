@echo off
:: Check for Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell Start-Process "%~0" -Verb RunAs
    exit /b
)

:: Check if SSHD service exists
sc query sshd >nul 2>&1
if %errorlevel% neq 0 (
    echo The SSHD service is not installed on this system.
    exit /b
)

:: Check if SSHD is running
sc query sshd | findstr /I "RUNNING"
if %errorlevel% equ 0 (
    echo SSHD service is already running.
) else (
    echo Starting SSHD service...
    net start sshd
    if %errorlevel% equ 0 (
        echo SSHD service started successfully.
    ) else (
        echo Failed to start SSHD service.
    )
)
