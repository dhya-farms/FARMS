#!/bin/bash

# Copy the Nginx configuration file to sites-available, ensuring the .conf extension is used
sudo cp -rf app.conf /etc/nginx/sites-available/

# Correctly setting permissions for the workspace directory
chmod 710 /var/lib/jenkins/workspace/FARMS

# Remove any existing symlink to avoid errors
sudo rm -f /etc/nginx/sites-enabled/app.conf

# Create a new symlink in sites-enabled for the Nginx configuration
sudo ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/

# Test the Nginx configuration for syntax errors
if sudo nginx -t; then
    echo "Nginx configuration is ok."

    # Reload Nginx to apply changes if it's already running, else start it
    if sudo systemctl is-active --quiet nginx; then
        echo "Reloading Nginx."
        sudo systemctl reload nginx
    else
        echo "Starting Nginx."
        sudo systemctl start nginx
    fi

    # Enable Nginx to start on boot
    sudo systemctl enable nginx

    echo "Nginx has been configured and reloaded."
else
    echo "Error in Nginx configuration."
    exit 1
fi

# Optionally, print the status of Nginx without pausing the script
sudo systemctl status nginx --no-pager
