import os
import subprocess

import requests
from requests.auth import HTTPBasicAuth
import jenkins

# Jenkins connection details
jenkins_url = os.getenv('JENKINS_URL')
username = os.getenv('JENKINS_USER')
api_token = os.getenv('JENKINS_PASS')  # Get it from Jenkins > User > Configure
jenkins_pat_token = os.getenv('PAT_JENKINS')
jenkins_credentials_id = os.getenv('JENKINS_CREDENTIALS_ID')

# ------------------------------- Methods -------------------------------

def create_ssh_key():
    # Generate an SSH key pair
    print("Generating an SSH key pair...")
    ssh_keygen = subprocess.run(['ssh-keygen', '-t', 'rsa', '-N', '', '-f', 'jenkins_rsa'], check=True)
    print("SSH key pair generated successfully.")

    # Read the public key
    with open('jenkins_rsa.pub', 'r') as public_key_file:
        public_key = public_key_file.read()

    return public_key

# ------------------------------- END Methods -------------------------------

# ------------------------------- Main -------------------------------

print(f"JENKINS INFO -> Jenkins URL: {jenkins_url}, Username: {username}, API Token: {api_token}")

# ----------- Generate SSH key pair -----------
create_ssh_key()

# Connect to the Jenkins server
jenkins_service = jenkins.Jenkins(jenkins_url, username, api_token)

# Jenkins version
user = jenkins_service.get_whoami()
version = jenkins_service.get_version()
print('JENKINS INFO -> Hello %s from Jenkins %s' % (user['fullName'], version))

# Node details
node_name = 'docker-node'
node_description = 'Node configured with Docker'
remote_fs = '/var/jenkins_home'
labels = 'docker'
num_executors = 2

# Script to install Docker on the node
install_docker_script = '''#!/bin/bash
if ! [ -x "$(command -v docker)" ]; then
    echo "Docker is not installed. Proceeding to install Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker jenkins  # Add the Jenkins user to the Docker group
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi
'''

# Node configuration with the Docker installation script
# node_config_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
# <slave>
#   <name>{node_name}</name>
#   <description>{node_description}</description>
#   <remoteFS>{remote_fs}</remoteFS>
#   <numExecutors>{num_executors}</numExecutors>
#   <mode>EXCLUSIVE</mode>
#   <retentionStrategy class="hudson.slaves.RetentionStrategy$Always"/>
#   <launcher class="hudson.slaves.CommandLauncher">
#     <command>{install_docker_script}</command>
#   </launcher>
#   <label>{labels}</label>
#   <nodeProperties/>
# </slave>'''
node_config_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<slave>
  <name>{node_name}</name>
  <description>{node_description}</description>
  <remoteFS>{remote_fs}</remoteFS>
  <numExecutors>{num_executors}</numExecutors>
  <mode>EXCLUSIVE</mode>
  <retentionStrategy class="hudson.slaves.RetentionStrategy$Always"/>
  <label>{labels}</label>
  <nodeProperties/>
</slave>'''

# Create the node in Jenkins
try:
    # List all nodes
    print(jenkins_service.get_nodes())
    if jenkins_service.node_exists(node_name):
        print(f"Node '{node_name}' already exists. Deleting it...")
        jenkins_service.delete_node(node_name)
    else:
        print(f"Node '{node_name}' does not exist.")
    print(f"Creating node '{node_name}' with Docker installation...")

    params = {
        'port': '22',
        'username': username,
        'credentialsId': jenkins_credentials_id,
        'host': 'host.docker.internal' # Is the host where jenkins docker is running
    }
    print("Creating node with parameters")
    jenkins_service.create_node(
        node_name,
        nodeDescription=node_description,
        remoteFS=remote_fs,
        labels=labels,
        exclusive=True,
        launcher=jenkins.LAUNCHER_SSH,
        launcher_params=params)

    print(f"Node '{node_name}' created successfully with Docker installation.")
    start_jenkins_agent = './start_jenkins_agent.sh'
    print(f'Now it will start the Jenkins agent with the following command: {start_jenkins_agent}')
    # subprocess.run(['bash', start_jenkins_agent], check=True)
    # print('Jenkins agent started successfully.')

except jenkins.JenkinsException as e:
    print(f"Error creating node: {e}")