# Use the Jenkins base image
FROM kolmanfreecss/jenkins-git:latest as jenkins-git

RUN echo "INIT Dockerfile"

# Switch to the root user to install packages
USER root

# Install necessary dependencies
RUN apt-get update && apt-get install -y python3-pip python3-venv

# Create a Python virtual environment within the container
RUN python3 -m venv /app/venv

# Copy the Python dependency file (if you have a requirements.txt)
COPY requirements.txt /app/

# Install Python dependencies in the virtual environment
RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Copy shell scripts and Python scripts to the container
#COPY shellscript/start_py_jenkins.sh /app/start_py_jenkins.sh
#COPY python/build.py /app/build.py

# Copy the shell script that installs dependencies
COPY jenkins_install_deps.sh /usr/local/bin/jenkins_install_deps.sh

# Ensure the shell scripts are executable
RUN chmod +x /usr/local/bin/jenkins_install_deps.sh

# Set the virtual environment as the default for Python
ENV PATH="/app/venv/bin:$PATH"

RUN echo "Before executing the shell script"

# Execute the dependency installation script
RUN /usr/local/bin/jenkins_install_deps.sh

RUN echo "After executing the shell script and before executing the Python script"

RUN ls -l /app

# Execute the copied shell script
#RUN /app/build.sh

RUN echo "After executing the Python script"