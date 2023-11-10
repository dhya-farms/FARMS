#!/bin/bash

# Delete the old Nginx configuration file, if it exists
sudo rm -f /etc/nginx/sites-available/FARMS.conf
sudo rm -f /etc/nginx/sites-enabled/FARMS.conf

# Copy the new Nginx configuration file
sudo cp FARMS.conf /etc/nginx/sites-available/FARMS.conf

# Create a symbolic link for Nginx
sudo ln -s /etc/nginx/sites-available/FARMS.conf /etc/nginx/sites-enabled/FARMS.conf

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
