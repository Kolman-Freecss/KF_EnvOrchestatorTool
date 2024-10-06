#!/bin/bash

# Detect Windows using Git Bash or WSL
if command -v cmd.exe &> /dev/null; then
    # If you're in Windows, adjust $HOME to a valid Windows path
    if [ -n "$USERPROFILE" ]; then
        SSH_KEY_PATH="$USERPROFILE/.ssh/id_rsa"
    else
        SSH_KEY_PATH="C:/Users/$(whoami)/.ssh/id_rsa"
    fi
else
    # If you're in a Unix-like environment, don't change anything
    SSH_KEY_PATH="$HOME/.ssh/id_rsa"
fi

echo "SH -> Path to generate SSH key: $SSH_KEY_PATH"

# Check if the SSH key already exists
if [ -f "$SSH_KEY_PATH" ]; then
    echo "SH -> SSH key already exists at $SSH_KEY_PATH"
else
    DIR_PATH="$(dirname "$SSH_KEY_PATH")"
    echo "Trying to create directory: $DIR_PATH"

    # Create the ~/.ssh directory if it doesn't exist
    if [ ! -d "$DIR_PATH" ]; then
        mkdir -p "$DIR_PATH" || { echo "Failed to create directory"; exit 1; }
        echo "Directory created: $DIR_PATH"
    else
        echo "Directory already exists: $DIR_PATH"
    fi

    # Generate an SSH key without a passphrase (-N "") and without interaction (-q)
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -q

    # Set the correct permissions
    chmod 600 "$SSH_KEY_PATH"
    chmod 644 "$SSH_KEY_PATH.pub"

    echo "SSH key generated at $SSH_KEY_PATH"
fi
