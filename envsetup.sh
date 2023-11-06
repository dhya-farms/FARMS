#!/bin/bash

# Remove the existing virtual environment if it exists and create a new one
if [ -d "env" ]
then
    echo "Python virtual environment exists. Removing and creating a new one."
    rm -rf env
fi

# Create a new virtual environment
python3 -m venv env
echo "Python virtual environment created."

echo "Current directory is: $PWD"

# Activate the virtual environment
source env/bin/activate

# Set environment variables here
export ENV_PATH=".env.prod"

# Update system package list and install system dependencies
sudo apt-get update
sudo apt-get install -y libpq-dev

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
# Note: Using 777 permissions is not recommended for security reasons
sudo chmod -R 777 logs

echo "envsetup is finished."
