# KF_EnvOrchestatorTool

This tool is used to serve an automated environment in local or cloud platform to easily develop applications monolith or any architecture, it doesn't matter.

# Index

- [Systems](#systems)
- [Getting Started](#getting-started)
- [Local installation](#local-installation)
    - [Configure Jenkins](#configure-jenkins)
    - [Configure Environment Variables to execute main.py](#configure-environment-variables-to-execute-mainpy)
    - [Configure SSH](#configure-ssh)
- [AWS Configuration](#aws-configuration)
    - [Trigger Terraform pipeline](#trigger-terraform-pipeline)
    - [Connect to EC2 instance](#connect-to-ec2-instance)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Tech stacks CI/CD](#tech-stacks-ci/cd)
- [Tips](#tips)
- [Troubleshoting](#troubleshoting)
    - [Jenkins](#jenkins)
    - [Scripts](#scripts)
    - [AWS](#aws)
    - [Settings](#settings)

# Systems

- Jenkins set up with docker-compose
- Automate Jenkins implantation on AWS with Terraform
- Automate Jenkins jobs with Python
- Execute local Jenkins with preconfigured plugins with a custom image on Docker Hub with Docker Compose.
- Github Actions to CI/CD with Jenkins.
- Second service to initialize Jenkins with Python and Shellscript.

# Getting Started

## Local installation

### Configure Jenkins

Config Jenkins on your local machine:

- Initial password located at `/var/jenkins_home/secrets/initialAdminPassword`

1. Execute `docker-compsoe.yml` from `.docker/local` folder.
2. Go to `localhost:8080` and follow the instructions to configure Jenkins. (Create an initialAdminPassword)
3. Install Git plugin for Jenkins. (This is necessary to trigger pipelines with SCM option enabled)

### Configure Environment Variables to execute main.py

1. Create a `local.env` file at `.env` folder.

Add the following variables:

```
JENKINS_URL=<YOUR_JENKINS_URL>
JENKINS_USER=<YOUR_JENKINS_USER>
JENKINS_PASS=<YOUR_JENKINS_PASSWORD>
ACCESS_TOKEN=<YOUR_GITHUB_ACCESS_TOKEN>
```

### Configure SSH

- Install OpenSSH Server on your local machine.
- Start the service.

```bash
# Windows
Start-Service sshd
```

- (Optional) Try to connect from container to your local machine with SSH.

```bash
docker exec -it jenkins-git bash
ssh -i /var/jenkins_home/.ssh/id_rsa admin@host.docker.internal -vvv
```

## AWS Configuration

Implantation of Jenkins automated with Terraform on AWS.

Requirements:

- Create your AWS account.
- Create your Access Key in the Security Credentials section.
- Take an AMI valid for your region.
- Configure SSH key pair in your AWS account for EC2 instances.
- Configure VPC.
- Configure Subnet.

1. Configure AWS CLI with your credentials:

```bash
aws configure

# AWS Access Key ID [None]: YOUR_ACCESS_KEY
# AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
```

2. Go to AMI Catalog and take an AMI ID for your region.

Put your AMI ID in `main.tf` file.

3. Configure your SSH key pair in `main.tf` file.

```bash
aws ec2 create-key-pair --key-name my-ssh-key --query 'KeyMaterial' --output text > my-ssh-key.pem
```

### Trigger Terraform pipeline

Project has different .tf files decoupled by behaviour. Terraform will treat all files as an unique project.

1. Init Terraform:

```bash
terraform init
```

2. Plan Terraform:

```bash
terraform plan
```

3. Apply Terraform:

```bash
terraform apply
```

4. Destroy Terraform:

```bash
terraform destroy
```

### Connect to EC2 instance

Here we've different ways to connect to EC2 instance:

1. Using SSH command:

```bash
# Create your SSH key pair previously in the EC2 AWS section.
ssh -i my-ssh-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

# Configuration

In this project, a Jenkins docker image was built and pushed to Docker Hub to store a basic archetypal Jenkins config
with Git, Docker and Pipeline plugins.

You can pulled it from Docker Hub with:

```bash
docker pull kolmanfreecss/jenkins-git
```

(Process to build the image and push it to Docker Hub)

1. Commit the current status container

```bash
docker commit YOUR_CONTAINER_ID kolmanfreecss/jenkins-git
```

2. Login to Docker Hub

```bash
docker login
```

3. Push the image to Docker Hub

```bash
docker push kolmanfreecss/jenkins-git
```

# Dependencies

- Jenkins API
    - Plugins:
        - Git (Check Configuration section)
        - Pipeline (Check Configuration section)
        - Docker (Check Configuration section)

# Tech stacks CI/CD

- Jenkins
- Docker & Docker Compose
- AWS
- Python
- Shellscript
- Terraform

# Tips

- Check Event Viewer on Windows to see if SSH Server is running properly.
  - `Applications and Services Logs > OpenSSH > Operational`
- Remember that Jenkins needs SSH private key and the local machine needs its public key to validate the connection stored in
  the `authorized_keys` file.

# Troubleshoting

## Jenkins
- Script to install Jenkins not working properly.
    - Alternative Solution: Connect through SSH to the EC2 instance and install Jenkins
      manually. (https://mirrors.jenkins.io/redhat-stable/)
        - After that connect to the IPv4 Public EC2 instance with HTTP protocol and port 8080.
            - Example: http://YOUR_EC2_PUBLIC_IP:8080
- Check EC2 system log from AWS section to see if Jenkins is running properly or installed.
- BIG Problems installing plugins https://community.jenkins.io/t/issue-while-upgrading-plugins-on-latest-jenkins/9846
    - It seems that halifax has blocked the ISP, so we need to install the plugins manually or use another ISP in order
      to install them.
        - https://community.jenkins.io/t/installing-suggested-plugins-in-jenkins-fails-due-to-connection-timed-out/12564
    - Another solution is to use a VPN to change the IP address and try to install the plugins again.
    - Another
      solution: https://stackoverflow.com/questions/77096022/jenkins-cli-to-install-jenkins-plugins-error-unknownhostexception
        - Manual installation of plugins. (https://www.jenkins.io/doc/book/managing/plugins/#advanced-installatio)
            - To install them to have Git for example you will need to install before Git plugin all its dependencies.
              Follow this order:
                1. https://plugins.jenkins.io/instance-identity/releases/
                2. https://plugins.jenkins.io/mailer/releases/
                3. https://plugins.jenkins.io/credentials/releases/
                4. https://plugins.jenkins.io/plain-credentials/releases/
                5. https://plugins.jenkins.io/variant/releases/
                6. https://plugins.jenkins.io/ssh-credentials/releases/
                7. https://plugins.jenkins.io/credentials-binding/releases/
                8. https://plugins.jenkins.io/git-client/releases/
- It takes its time to start even if the instance is running. Be patient. :)
    - Check logs with
        - ```bash
      aws ec2 get-console-output --instance-id YOUR_INSTANCE_ID --output text
      ```
      
## Scripts

- Use `dos2unix` to convert the scripts to Unix format.
    - ```bash
      dos2unix YOUR_SCRIPT.helpers
      ```
- Create SSH credentials on Jenkins through Python with Jenkins API. Problem with the XML tag using incorrect format for the implementation
  - Solution: Use `com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey`
      
## AWS
- Check SSH key permissions to connect to EC2 instance.
    - `chmod 400 my-ssh-key.pem`
    - Remove permissions to other group users or another users because AWS won't let you connect to the EC2 instance if
      the permissions are too permissive.

## Settings
- Install SSH Server on local machine.
    - If you have a Windows Server you can follow Microsoft official documentation to install OpenSSH Server. Or check https://github.com/PowerShell/Win32-OpenSSH/releases
    - Also you could use WSL to install OpenSSH Server.
      - ```bash
        sudo apt-get install openssh-server
        ```
    - Configure permissions to the id_rsa file to not be too permissive.
        - ```bash
          chmod 600 /var/jenkins_home/.ssh/id_rsa
          ```
    - Create an authorized_keys file in the .ssh folder with the public key of the local machine.
        - ```bash
          cat /var/jenkins_home/.ssh/id_rsa.pub >> /var/jenkins_home/.ssh/authorized_keys
          ```
    - Create an sshd_config file in the .ssh folder with the following IMPORTANT configurations UNCCOMMENTED.:
        - ```bash
          Port 22
          AuthorizedKeysFile /var/jenkins_home/.ssh/authorized_keys
          PubkeyAuthentication yes
          PasswordAuthentication no
          ```

---

Shield: [![CC-BY-NC-ND 4.0][CC-BY-NC-ND-shield]][CC-BY-NC-ND]

This work is licensed under
a [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.][CC-BY-NC-ND]

[![CC-BY-NC-ND 4.0][CC-BY-NC-ND-image]][CC-BY-NC-ND]

[CC-BY-NC-ND-shield]: https://img.shields.io/badge/License-CC--BY--NC--ND--4.0-lightgrey

[CC-BY-NC-ND]: http://creativecommons.org/licenses/by-nc-nd/4.0/

[CC-BY-NC-ND-image]: https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png
