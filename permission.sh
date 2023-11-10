#!/bin/bash

# Set the base directory for the project
BASE_DIR="/var/lib/jenkins/workspace/FARMS"

# Create the 'nginx' group if it doesn't exist and add users to it
sudo groupadd nginx
sudo usermod -a -G nginx root
sudo usermod -a -G nginx www-data
sudo usermod -a -G nginx jenkins

# Change the group ownership of the project directory and its contents to 'nginx'
sudo chown -R root:nginx /var/lib/jenkins

# Set the appropriate permissions
sudo chmod 755 /var/lib/jenkins
sudo chmod 755 /var/lib/jenkins/workspace
sudo chmod 770 -R "$BASE_DIR"

# If there are specific subdirectories within the project that need different permissions, set them here
sudo chmod 770 -R "$BASE_DIR/staticfiles"
sudo chmod 770 -R "$BASE_DIR/app"
sudo chmod 770 -R "$BASE_DIR/FARMS"


sudo ufw allow 80
sudo ufw allow 443