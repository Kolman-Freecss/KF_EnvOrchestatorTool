import os
import platform
import subprocess
from enum import Enum

import jenkins
import requests

import config as config_module

print(f"Connecting to Jenkins. Connection Data -> URL: {config_module.get(config_module.ConfigKeys.JENKINS_URL)}, User: {config_module.get(config_module.ConfigKeys.JENKINS_USER)}, API Token: {config_module.get(config_module.ConfigKeys.JENKINS_PASS)}")

try:
    # Connect to the Jenkins server
    jenkins_service = jenkins.Jenkins(config_module.get(config_module.ConfigKeys.JENKINS_URL),
                                      config_module.get(config_module.ConfigKeys.JENKINS_USER),
                                      config_module.get(config_module.ConfigKeys.JENKINS_PASS))
except Exception as e:
    print(f"Error connecting to Jenkins: {e}")

class CredentialsType(str, Enum):
    USER = 'USER'
    SSH = 'SSH'

def get_jenkins_crumb() -> tuple[str, str]:
    """
    Get Jenkins crumb to add to headers
    :return: Tuple with crumb field and crumb value
    """
    crumb_url = f'{config_module.config.get(config_module.ConfigKeys.JENKINS_URL)}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)'
    print("Crumb data: URL: ", crumb_url, " User: ", config_module.config.get(config_module.ConfigKeys.JENKINS_USER), " Pass: ", config_module.config.get(config_module.ConfigKeys.JENKINS_PASS))
    crumb_response = requests.get(
        crumb_url,
        auth=(config_module.config.get(config_module.ConfigKeys.JENKINS_USER), config_module.config.get(config_module.ConfigKeys.JENKINS_PASS))
    )

    if crumb_response.status_code != 200:
        print("Error fetching crumb -> Received status code: ", crumb_response.status_code, " with message: ", crumb_response.text)
        exit(1)

    # Parse crumb response
    crumb_field, crumb_value = crumb_response.text.split(':')
    print(f'Crumb field: {crumb_field}, Crumb value: {crumb_value}. Original response -> {crumb_response.text}')
    return crumb_field, crumb_value

def build_user_credentials() -> any:
    """
    Create username/password credentials in Jenkins
    :return:
    """

    id_value = f"{config_module.config.get(config_module.ConfigKeys.JENKINS_CREDENTIALS_ID)}-user"
    description_value = f"Credentials to access GitHub with PAT with {id_value}"
    credentials = f'''<?xml version='1.1' encoding='UTF-8'?>
    <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
      <scope>GLOBAL</scope>
      <id>{id_value}</id>
      <username>{config_module.config.get(config_module.ConfigKeys.JENKINS_USER)}</username>
      <password>{config_module.config.get(config_module.ConfigKeys.PAT_JENKINS)}</password>
      <description>{description_value}</description>
    </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
    '''
    return credentials

def build_ssh_credentials(force: bool = False) -> any:
    """
    Create SSH credentials in Jenkins
    :param force: Flag to force the creation of credentials even if they already exist
    :return:
    """
    private_key = get_ssh(force)

    id_value = f"{config_module.config.get(config_module.ConfigKeys.AGENT_CREDENTIALS_SSH)}"
    description_value = f"SSH Credentials to access GitHub with {id_value}"
    credentials = f'''<?xml version='1.1' encoding='UTF-8'?>
    <com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>
      <scope>GLOBAL</scope>
      <id>{id_value}</id>
      <username>{config_module.config.get(config_module.ConfigKeys.JENKINS_USER)}</username>
      <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
        <privateKey>{private_key}</privateKey>
      </privateKeySource>
      <description>{description_value}</description>
    </com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>
    '''
    print(f'BUILD SSH CREDENTIALS:: XML Document: ***** ') # {credentials}')
    return credentials

def build_credentials(credential_type: CredentialsType, force: bool = False) -> any:
    """
    Create credentials in Jenkins based on the type specified
    :param force:  Flag to force the creation of credentials even if they already exist
    :param credential_type: CredentialType Enum specifying the type of credentials
    :return:
    """
    print(f'build_credentials:: Building credentials: {credential_type}')
    # Determine which credentials to build based on the credential_type
    if credential_type == CredentialsType.USER:
        credentials = build_user_credentials()
    elif credential_type == CredentialsType.SSH:
        credentials = build_ssh_credentials(force)
    else:
        raise ValueError("Unsupported credential type")

# TODO: Add crumb to headers working or API Token automated
    # print(f'build_credentials:: Fetching Jenkins crumb... to build Credentials: {credential_type}')
    # crumb_field, crumb_value = get_jenkins_crumb()

    response = requests.post(
        f'{config_module.config.get(config_module.ConfigKeys.JENKINS_URL)}/credentials/store/system/domain/_/createCredentials',
        auth=(config_module.config.get(config_module.ConfigKeys.JENKINS_USER), config_module.config.get(config_module.ConfigKeys.JENKINS_API_TOKEN)),
        data=credentials,
        headers={
            'Content-Type': 'application/xml',
            # crumb_field: crumb_value  # Add crumb to headers
        }
    )

    # jenkins_service.create_credential(folder_name='system', config_xml=credentials, domain_name='')

    if response.status_code == 200:
        print('Credentials created successfully')
    elif not force:
        print(f'ERROR creating credentials status code: {response.status_code}, message: {response.text}, \n retrying with force flag')
        build_credentials(credential_type, force=True)
    else:
        print(f'ERROR creating credentials status code: {response.status_code}, message: {response.text}')

def get_ssh(force: bool = False) -> str:
    """
    Get SSH credentials
    :return: Private key if it exists; otherwise, generates a new one and returns it.
    """
    ssh_dir = os.path.expanduser('~/.ssh')
    ssh_key_path = os.path.join(ssh_dir, 'id_rsa')

    if os.path.exists(ssh_key_path) and os.path.getsize(ssh_key_path) > 0 and not force:
        try:
            with open(ssh_key_path, 'r') as private_key_file:
                private_key = private_key_file.read()
                print("Private key found.")
                return private_key
        except FileNotFoundError:
            print(f"Private key not found at {ssh_key_path}. Generating a new key.")
            return create_ssh()
    else:
        if force:
            print(f"Force flag set. Generating a new key.")
        else:
            print(f"No SSH key found at {ssh_key_path}. Generating a new key.")
        return create_ssh(force)

def create_ssh(force: bool = False) -> str:
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
    if os.path.exists(ssh_key_path) and os.path.getsize(ssh_key_path) > 0 and not force:
        print(f"SSH key pair already exists at {ssh_key_path}.")
        return get_ssh()  # Return the existing key

    if force:
        print("Force flag set. Deleting existing SSH key pair.")
        os.remove(ssh_key_path)

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

def start_ssh_server():
    """
    Start the SSH server
    """
    print("Starting SSH server...")
    script_path = 'helpers/start_ssh_server.sh'

    # Check the OS and run the corresponding script
    if platform.system() == 'Windows':
        script_path = os.path.abspath('helpers/start_ssh_server.bat')
        print(f"Running the batch script: {script_path}")
        # Execute the batch script for Windows
        subprocess.run([script_path], check=True, shell=True)
    else:
        print(f"Running the shell script: {script_path}")
        # Execute the shell script for Unix-like environments
        subprocess.run(['bash', script_path], check=True)

    print("SSH server started successfully.")