import os

import config as config_module
import services as services
from services import CredentialsType

def fetch():
    try:
        print(f"JENKINS INFO -> Jenkins URL: {config_module.get(config_module.ConfigKeys.JENKINS_URL)}, Username: {config_module.get(config_module.ConfigKeys.JENKINS_USER)}, API Token: {config_module.get(config_module.ConfigKeys.JENKINS_PASS)}")

        # Jenkins version
        user = services.jenkins_service.get_whoami()
        version = services.jenkins_service.get_version()
        print('JENKINS INFO -> Hello %s from Jenkins %s' % (user['fullName'], version))

        # Print all files in the current directory
        print(os.listdir('.'))

        # Configured on docker-compose (check volumes)
        if config_module.ENV == 'local' or config_module.ENV == 'docker-env':
            path_job = '../.data/Jenkinsfile_spring.xml'
        else:
            path_job = './data/Jenkinsfile_spring.xml'

        # List all content dir
        if config_module.ENV != 'local' or config_module.ENV != 'docker-env':
            try:
                content = os.listdir('../')
                print(content)
            except Exception as e:
                print(e)

        # Read XML job
        job_config = open(path_job).read()

        # Create credentials
        services.build_credentials(CredentialsType.USER)

        job_name = "spring-pipeline"

        try:
            if services.jenkins_service.job_exists(job_name):
                services.jenkins_service.delete_job(job_name)
                print(f'Job {job_name} already exists and was deleted')
            else:
                print(f'Job {job_name} does not exist')
            services.jenkins_service.create_job(job_name, job_config)
            print('Job created successfully')
        except Exception as e:
            print(e)

        services.jenkins_service.build_job(job_name)
        print('Job execute successfully')
    except Exception as e:
        print("Error: ", e)

def start():
    print("Build:: ...")
    try:
        fetch()
    except Exception as e:
        print("Error: ", e)

if config_module.ENV == 'local':
    start()