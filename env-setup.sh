#!/bin/bash

# Check if the virtual environment directory exists
if [ -d "env" ]
then
    echo "Python virtual environment exists."
else
    python3 -m venv env
    echo "Python virtual environment created."
fi

echo "Current directory is: $PWD"

# Activate the virtual environment
source env/bin/activate

# Set environment variables here
export ENV_PATH=".env.prod"

# Install Python dependencies
pip3 install -r requirements.txt

# Check if the logs directory exists and create it if it doesn't
if [ -d "logs" ]
then
    echo "Log folder exists."
else
    sudo mkdir logs
    sudo touch logs/django_server_stderr.log logs/gunicorn_stderr.log logs/nginx_access.log logs/openai_worker_stderr.log logs/django_server_stdout.log logs/gunicorn_stdout.log logs/nginx_error.log logs/openai_worker_stdout.log
    echo "Log folders created."
fi

echo "envsetup is finished."

sudo chmod -R 777 logs
