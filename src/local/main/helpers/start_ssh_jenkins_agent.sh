#!/bin/bash

# Start the sshd service
sudo systemctl start sshd

# Check if the sshd service is running
service_status=$(systemctl is-active sshd)

# Log the service status to a file
echo "The sshd service is in status: $service_status" >> sshd_service_log.txt

# Display the status on the screen
echo "The sshd service is in status: $service_status"
