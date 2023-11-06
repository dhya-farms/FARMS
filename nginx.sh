#!/bin/bash

# Copy the Nginx configuration file to sites-available, ensuring the .conf extension is used
sudo cp -rf app.conf /etc/nginx/sites-available/

# Correctly setting permissions for the workspace directory
chmod 710 /var/lib/jenkins/workspace/FARMS

# Create a symlink in sites-enabled for the Nginx configuration
# First, remove any existing symlink to avoid errors
sudo rm -f /etc/nginx/sites-enabled/app.conf
sudo ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/

# Test the Nginx configuration for syntax errors
sudo nginx -t

# Start Nginx if it's not already running, reload it to apply changes, and enable it to start on boot
sudo systemctl start nginx
sudo systemctl reload nginx
sudo systemctl enable nginx

echo "Nginx has been started"

# Optionally check the status of Nginx, but note that this will cause the script to pause until you exit the status screen
sudo systemctl status nginx
