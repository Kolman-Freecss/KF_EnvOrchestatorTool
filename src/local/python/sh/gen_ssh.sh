#!/bin/bash

# Path where the SSH key will be stored (you can change this if needed)
SSH_KEY_PATH="$HOME/.ssh/id_rsa"

# Check if the SSH key already exists
if [ -f "$SSH_KEY_PATH" ]; then
    echo "SSH key already exists at $SSH_KEY_PATH"
else
    # Create the ~/.ssh directory if it doesn't exist
    mkdir -p "$HOME/.ssh"

    # Generate an SSH key without a passphrase (-N "") and without interaction (-q)
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -q

    # Set the correct permissions
    chmod 600 "$SSH_KEY_PATH"
    chmod 644 "$SSH_KEY_PATH.pub"

    echo "SSH key generated at $SSH_KEY_PATH"
fi
