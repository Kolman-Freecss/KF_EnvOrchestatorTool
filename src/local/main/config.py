import os
from dotenv import dotenv_values

from enum import Enum

class ConfigKeys(str, Enum):
    JENKINS_URL = 'JENKINS_URL'
    JENKINS_USER = 'JENKINS_USER'
    JENKINS_PASS = 'JENKINS_PASS'
    PAT_JENKINS = 'PAT_JENKINS'
    JENKINS_CREDENTIALS_ID = 'JENKINS_CREDENTIALS_ID'
    AGENT_CREDENTIALS_SSH = 'AGENT_CREDENTIALS_SSH'


# Global variables
config = {}
ENV = os.getenv('ENV') # Provided by Github Actions or Environment Variables
if ENV == 'prod':
    env_files_path = '<cloud-config>'
else:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    env_files_path = os.path.join(project_root, '.env', f'env.{ENV}')
    ENV = 'local'

# Sensitive data not injected through pipelines
config = dotenv_values(env_files_path)

if ENV == 'prod':
    # Jenkins connection details
    jenkins_url = os.getenv(ConfigKeys.JENKINS_URL.value)
    jenkins_username = os.getenv(ConfigKeys.JENKINS_USER.value)
    jenkins_password = os.getenv(ConfigKeys.JENKINS_PASS.value)  # Get it from Jenkins > User > Configure
    jenkins_pat_token = os.getenv(ConfigKeys.PAT_JENKINS.value)
    jenkins_credentials_id = os.getenv(ConfigKeys.JENKINS_CREDENTIALS_ID.value)
    agent_credentials_ssh = os.getenv(ConfigKeys.AGENT_CREDENTIALS_SSH.value)

    # Storing values in the config dictionary
    config[ConfigKeys.JENKINS_URL.value] = jenkins_url
    config[ConfigKeys.JENKINS_USER.value] = jenkins_username
    config[ConfigKeys.JENKINS_PASS.value] = jenkins_password
    config[ConfigKeys.PAT_JENKINS.value] = jenkins_pat_token
    config[ConfigKeys.JENKINS_CREDENTIALS_ID.value] = jenkins_credentials_id
    config[ConfigKeys.AGENT_CREDENTIALS_SSH.value] = agent_credentials_ssh

def get(key: str) -> str:
    return config.get(key)