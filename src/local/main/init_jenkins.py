import platform
import subprocess

import jenkins

import config as config_module
import services as services
from services import CredentialsType


def fetch():
    # ------------------------------- Main -------------------------------

    print(f"JENKINS INFO -> Jenkins URL: {config_module.get(config_module.ConfigKeys.JENKINS_URL)}, Username: {config_module.get(config_module.ConfigKeys.JENKINS_USER)}, API Token: {config_module.get(config_module.ConfigKeys.JENKINS_PASS)}")

    # ----------- Generate SSH key pair -----------
    print('Getting SSH key...')
    services.get_ssh() # Get the private key from the SSH key pair to connect Jenkins node via SSH to the agent (machine defined)
    services.build_credentials(CredentialsType.SSH)

    # Jenkins version
    user = services.jenkins_service.get_whoami()
    version = services.jenkins_service.get_version()
    print('JENKINS INFO -> Hello %s from Jenkins %s' % (user['fullName'], version))

    # Node details
    node_name = 'docker-node'
    node_description = 'Node configured with Docker'
    remote_fs = '/var/jenkins_home'
    labels = 'docker'

    # Create the node in Jenkins
    try:
        # List all nodes
        print(services.jenkins_service.get_nodes())
        if services.jenkins_service.node_exists(node_name):
            print(f"Node '{node_name}' already exists. Deleting it...")
            services.jenkins_service.delete_node(node_name)
        else:
            print(f"Node '{node_name}' does not exist.")
        print(f"Creating node '{node_name}' with Docker installation...")

        ssh_port = 22
        ssh_user = config_module.get(config_module.ConfigKeys.JENKINS_USER)
        ssh_credentials = config_module.get(config_module.ConfigKeys.AGENT_CREDENTIALS_SSH)
        ssh_agent_host = 'host.docker.internal'  # Is the host where Jenkins Docker is running
        print(f"SSH data -> Port: {ssh_port}, User: {ssh_user}, Credentials: {ssh_credentials}, Host: {ssh_agent_host}")

        params = {
            'port': ssh_port,
            'username': ssh_user,
            'credentialsId': ssh_credentials,
            'host': ssh_agent_host
        }
        print("Creating node with parameters")
        services.jenkins_service.create_node(
            node_name,
            nodeDescription=node_description,
            remoteFS=remote_fs,
            labels=labels,
            exclusive=True,
            launcher=jenkins.LAUNCHER_SSH,
            launcher_params=params)

        print(f"Node '{node_name}' created successfully with Docker installation.")

        start_ssh_jenkins_agent = './helpers/start_ssh_jenkins_agent.sh'
        print(f'Now it will start the Jenkins agent with the following command: {start_ssh_jenkins_agent}')
        # Check the OS and run the corresponding script
        if platform.system() == 'Windows':
            start_ssh_jenkins_agent = './helpers/start_ssh_jenkins_agent.bat'
            print(f"Running the batch script: {start_ssh_jenkins_agent}")
            # Execute the batch script for Windows
            subprocess.run([start_ssh_jenkins_agent], check=True, shell=True)
        else:
            print(f"Running the shell script: {start_ssh_jenkins_agent}")
            subprocess.run(['bash', start_ssh_jenkins_agent], check=True)

    except jenkins.JenkinsException as e:
        print(f"Error creating node: {e}")

def start():
    print("Init_jenkins:: ...")
    try:
        fetch()
    except Exception as e:
        print("Error: ", e)

if config_module.ENV == 'local':
    start()