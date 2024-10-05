import os

import jenkins
import requests

jenkins_url = os.getenv('JENKINS_URL')
username = os.getenv('JENKINS_USER')
api_token = os.getenv('JENKINS_PASS')  # Get it from Jenkins > User > Configure
github_pat = os.getenv('PAT_JENKINS')
github_credentials_id = os.getenv('GITHUB_CREDENTIALS_ID')
github_user = os.getenv('GITHUB_USER')
# TODO: Do this more clean
execution_environment = os.getenv('EXECUTION_ENVIRONMENT')

try:
    print(f"JENKINS INFO -> Jenkins URL: {jenkins_url}, Username: {username}, API Token: {api_token}")
    jenkins_service = jenkins.Jenkins(jenkins_url, username, api_token)

    # Jenkins version
    user = jenkins_service.get_whoami()
    version = jenkins_service.get_version()
    print('JENKINS INFO -> Hello %s from Jenkins %s' % (user['fullName'], version))

    # Print all files in the current directory
    print(os.listdir('.'))

    # Configured on docker-compose (check volumes)
    if execution_environment == 'local':
        path_job = '../.data/Jenkinsfile_spring.xml'
    else:
        path_job = './data/Jenkinsfile_spring.xml'

    # List all content dir
    if execution_environment != 'local':
        try:
            content = os.listdir('../')
            print(content)
        except Exception as e:
            print(e)

    # Read XML job
    job_config = open(path_job).read()

    # Obtain crumb to add to headers (New need for Jenkins LTS)
    crumb_response = requests.get(
        f'{jenkins_url}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)',
        auth=(username, api_token)
    )

    if crumb_response.status_code != 200:
        print("Error fetching crumb:", crumb_response.text)
        exit(1)

    # Parse crumb response
    crumb_field, crumb_value = crumb_response.text.split(':')

    # ----------- Create credentials -----------
    credentials = f'''<?xml version='1.1' encoding='UTF-8'?>
    <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
      <scope>GLOBAL</scope>
      <id>{github_credentials_id}</id>
      <username>{github_user}</username>
      <password>{github_pat}</password>
      <description>Credentials to access Github with PAT</description>
    </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
    '''

    response = requests.post(
        f'{jenkins_url}/credentials/store/system/domain/_/createCredentials',
        # auth=(username, api_token),
        auth=(username, '11697578e5ce0fe728643fb9e5a5ad120f'),
        data=credentials,
        headers={
            'Content-Type': 'application/xml',
            'crumbHeaderName': crumb_value  # Add crumb to headers
        }
    )

    if response.status_code == 200:
        print('Credentials created successfully')
    else:
        print(f'Error creating credentials: {response.text}')

    job_name = "spring-pipeline"

    try:
        if jenkins_service.job_exists(job_name):
            jenkins_service.delete_job(job_name)
            print(f'Job {job_name} already exists and was deleted')
        else:
            print(f'Job {job_name} does not exist')
        jenkins_service.create_job(job_name, job_config)
        print('Job created successfully')
    except Exception as e:
        print(e)

    jenkins_service.build_job(job_name)
    print('Job execute successfully')
except Exception as e:
    print("Error: ", e)
