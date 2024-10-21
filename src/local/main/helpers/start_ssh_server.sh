#!/bin/bash

# Function to check if the script is being run as root
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "This script must be run as root. Please try again with sudo or as root."
        exit 1
    fi
}

# Check if running as root
check_root

# Check if the SSHD service is installed
if ! systemctl list-units --type=service --all | grep -q 'sshd.service'; then
    echo "The SSHD service is not installed on this system."
    exit 1
fi

# Check if SSHD is running
if systemctl is-active --quiet sshd; then
    echo "SSHD service is already running."
else
    echo "Starting SSHD service..."
    systemctl start sshd
    if [ $? -eq 0 ]; then
        echo "SSHD service started successfully."
    else
        echo "Failed to start SSHD service."
    fi
fi
