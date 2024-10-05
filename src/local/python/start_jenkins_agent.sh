#!/bin/bash

# Start the SSH server
sudo service ssh start

# Check status
if sudo service ssh status | grep -q 'running'; then
    echo "SSH server is running on port 22."
else
    echo "Failed to start SSH server."
fi
