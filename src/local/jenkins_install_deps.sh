#!/bin/bash
set -e

echo "Installation of Docker..."

# Update and install dependencies
apt-get update && \
apt-get install -y apt-transport-https ca-certificates curl software-properties-common && \
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
echo "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
apt-get update && \
apt-get install -y docker-ce docker-ce-cli containerd.io

echo "Docker installed!"

# Add jenkins user to docker group
usermod -aG docker jenkins

echo "Jenkins user added to Docker group. Please log out and back in for changes to take effect."
