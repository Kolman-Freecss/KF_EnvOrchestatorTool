import os
import platform
import subprocess
from enum import Enum

import jenkins
import requests

import src.local.main.config as config_module

# Connect to the Jenkins server
jenkins_service = jenkins.Jenkins(config_module.get(config_module.ConfigKeys.JENKINS_URL),
                                  config_module.get(config_module.ConfigKeys.JENKINS_USER),
                                  config_module.get(config_module.ConfigKeys.JENKINS_PASS))

class CredentialsType(str, Enum):
    USER = 'USER'
    SSH = 'SSH'

def get_jenkins_crumb() -> tuple[str, str]:
    """
    Get Jenkins crumb to add to headers
    :return: Tuple with crumb field and crumb value
    """
    crumb_response = requests.get(
        f'{config_module.config.get(config_module.ConfigKeys.JENKINS_URL)}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)',
        auth=(config_module.config.get(config_module.ConfigKeys.JENKINS_USER), config_module.config.get(config_module.ConfigKeys.PAT_JENKINS))
    )

    if crumb_response.status_code != 200:
        print("Error fetching crumb:", crumb_response.text)
        exit(1)

    # Parse crumb response
    crumb_field, crumb_value = crumb_response.text.split(':')
    return crumb_field, crumb_value

def build_user_credentials() -> any:
    """
    Create username/password credentials in Jenkins
    :return:
    """
    credentials = f'''<?xml version='1.1' encoding='UTF-8'?>
    <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
      <scope>GLOBAL</scope>
      <id>{config_module.config.get(config_module.ConfigKeys.JENKINS_CREDENTIALS_ID)}</id>
      <username>{config_module.config.get(config_module.ConfigKeys.JENKINS_USER)}</username>
      <password>{config_module.config.get(config_module.ConfigKeys.PAT_JENKINS)}</password>
      <description>Credentials to access GitHub with PAT</description>
    </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
    '''
    return credentials

def build_ssh_credentials() -> any:
    """
    Create SSH credentials in Jenkins
    :return:
    """
    private_key = get_ssh()

    credentials = f'''<?xml version='1.1' encoding='UTF-8'?>
    <com.cloudbees.plugins.credentials.impl.SSHUserPrivateKey>
      <scope>GLOBAL</scope>
      <id>{config_module.config.get(config_module.ConfigKeys.JENKINS_CREDENTIALS_ID)}</id>
      <username>{config_module.config.get(config_module.ConfigKeys.JENKINS_USER)}</username>
      <privateKey>{private_key}</privateKey>
      <description>SSH Credentials to access GitHub</description>
    </com.cloudbees.plugins.credentials.impl.SSHUserPrivateKey>
    '''
    return credentials


def build_credentials(credential_type: CredentialsType) -> any:
    """
    Create credentials in Jenkins based on the type specified
    :param credential_type: CredentialType Enum specifying the type of credentials
    :return:
    """
    # Determine which credentials to build based on the credential_type
    if credential_type == CredentialsType.USER:
        credentials = build_user_credentials()
    elif credential_type == CredentialsType.SSH:
        credentials = build_ssh_credentials()
    else:
        raise ValueError("Unsupported credential type")

    crumb_field, crumb_value = get_jenkins_crumb()

    response = requests.post(
        f'{config_module.config.get(config_module.ConfigKeys.JENKINS_URL)}/credentials/store/system/domain/_/createCredentials',
        auth=(config_module.config.get(config_module.ConfigKeys.JENKINS_USER), config_module.config.get(config_module.ConfigKeys.PAT_JENKINS)),
        data=credentials,
        headers={
            'Content-Type': 'application/xml',
            crumb_field: crumb_value  # Add crumb to headers
        }
    )

    if response.status_code == 200:
        print('Credentials created successfully')
    else:
        print(f'Error creating credentials: {response.text}')

def get_ssh() -> str:
    """
    Get SSH credentials
    :return: Private key if it exists; otherwise, generates a new one and returns it.
    """
    ssh_dir = os.path.expanduser('~/.ssh')
    ssh_key_path = os.path.join(ssh_dir, 'id_rsa')

    if os.path.exists(ssh_key_path) and os.path.getsize(ssh_key_path) > 0:
        try:
            with open(ssh_key_path, 'r') as private_key_file:
                private_key = private_key_file.read()
                print("Private key found.")
                return private_key
        except FileNotFoundError:
            print(f"Private key not found at {ssh_key_path}. Generating a new key.")
            return create_ssh()
    else:
        print(f"No SSH key found at {ssh_key_path}. Generating a new key.")
        return create_ssh()



def create_ssh() -> str:
    """
    Generate an SSH key pair if it does not exist.
    :return: The private key as a string. None if the private key is not found.
    """
    ssh_dir = os.path.expanduser('~/.ssh')
    ssh_key_path = os.path.join(ssh_dir, 'id_rsa')

    # Ensure the .ssh directory exists
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir)
        print(f"Directory {ssh_dir} created.")

    # Check if the SSH key already exists
    if os.path.exists(ssh_key_path) and os.path.getsize(ssh_key_path) > 0:
        print(f"SSH key pair already exists at {ssh_key_path}.")
        return get_ssh()  # Return the existing key

    print("Generating an SSH key pair...")
    script_path = 'helpers/gen_ssh.sh'

    # Check the OS and run the corresponding script
    if platform.system() == 'Windows':
        script_path = os.path.abspath('helpers/gen_ssh.bat')
        print(f"Running the batch script: {script_path}")
        # Execute the batch script for Windows
        subprocess.run([script_path], check=True, shell=True)
    else:
        print(f"Running the shell script: {script_path}")
        # Execute the shell script for Unix-like environments
        subprocess.run(['bash', script_path], check=True)

    print("SSH key pair generated successfully.")

    # Attempt to read the generated private key
    try:
        with open(ssh_key_path, 'r') as private_key_file:
            private_key = private_key_file.read()
            print("Private key generated and read successfully.")
            return private_key
    except FileNotFoundError:
        print(f"Private key not found at {ssh_key_path}.")
        return ""