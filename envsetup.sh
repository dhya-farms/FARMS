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

# Install system dependencies
sudo apt-get update && sudo apt-get install -y libpq-dev gcc
sudo rm -rf /var/lib/apt/lists/*
sudo apt-get clean

# Install Python dependencies
pip3 install -r requirements.txt

# Check if the logs directory exists and create it if it doesn't
if [ -d "logs" ]
then
    echo "Log folder exists."
else
    mkdir logs
    touch logs/error.log logs/access.log
    echo "Log folders created."
fi

# Set the permissions for the logs directory
sudo chmod -R 777 logs

echo "envsetup is finished."
