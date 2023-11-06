#!/bin/bash

sudo cp -rf FARMS.conf /etc/nginx/sites-available/FARMS
chmod 710 /var/lib/jenkins/workspace/FARMS

sudo ln -s /etc/nginx/sites-available/FARMS /etc/nginx/sites-enabled
sudo nginx -t

sudo systemctl start nginx
sudo systemctl enable nginx

echo "Nginx has been started"

sudo systemctl status nginx