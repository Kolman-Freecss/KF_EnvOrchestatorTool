@echo off
REM Start the sshd service
powershell -Command "Start-Service sshd"

REM Check if the sshd service is running
powershell -Command "Get-Service sshd | Select-Object Status"

REM Save the service status to a variable for logging
for /f "tokens=2 delims= " %%a in ('powershell -Command "Get-Service sshd | Select-Object -ExpandProperty Status"') do set status=%%a

REM Log the service status to a file
echo The sshd service is in status: %status% >> sshd_service_log.txt

REM Display the status on the screen
echo The sshd service is in status: %status%

pause
