@echo off
setlocal

echo Start...

REM Detect if we're on Windows and set the SSH key path
set "SSH_KEY_PATH=%USERPROFILE%\.ssh\id_rsa"

REM Show the path where the SSH key will be generated
echo Path to generate SSH key: %SSH_KEY_PATH%

REM Check if the SSH key already exists
if exist "%SSH_KEY_PATH%" (
    echo SSH key already exists at %SSH_KEY_PATH%
) else (
    REM Create the .ssh directory if it doesn't exist
    if not exist "%USERPROFILE%\.ssh" (
        mkdir "%USERPROFILE%\.ssh"
        echo Directory created: %USERPROFILE%\.ssh
    ) else (
        echo Directory already exists: %USERPROFILE%\.ssh
    )

    REM Generate an SSH key without a passphrase (-N "") and without interaction (-q)
    ssh-keygen -t rsa -b 4096 -f "%SSH_KEY_PATH%" -N "" -q

    REM Show success message
    echo SSH key generated at %SSH_KEY_PATH%
)

endlocal
