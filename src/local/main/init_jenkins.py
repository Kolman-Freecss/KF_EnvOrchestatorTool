import jenkins

import config as config_module
import services as services
from services import CredentialsType


def fetch():
    # ------------------------------- Main -------------------------------

    print(f"JENKINS INFO -> Jenkins URL: {config_module.get(config_module.ConfigKeys.JENKINS_URL)}, Username: {config_module.get(config_module.ConfigKeys.JENKINS_USER)}, API Token: {config_module.get(config_module.ConfigKeys.JENKINS_PASS)}")

    # ----------- Generate SSH key pair -----------
    print('Getting SSH key...')
    private_key = services.get_ssh() # Get the private key from the SSH key pair to connect Jenkins node via SSH to the agent (machine defined)
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
    num_executors = 2

    # Script to install Docker on the node
    install_docker_script = '''#!/bin/bash
    if ! [ -x "$(command -v docker)" ]; then
        echo "Docker is not installed. Proceeding to install Docker..."
        curl -fsSL https://get.docker.com -o get-docker.helpers
        helpers get-docker.helpers
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

        # TODO: Init SSH Client on agent host
        start_jenkins_agent = './start_jenkins_agent.helpers'
        print(f'Now it will start the Jenkins agent with the following command: {start_jenkins_agent}')
        # subprocess.run(['bash', start_jenkins_agent], check=True)
        # print('Jenkins agent started successfully.')

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