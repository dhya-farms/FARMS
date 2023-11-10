# Create a new group called 'nginx'
sudo groupadd nginx

# Add 'www-data', 'root', and 'jenkins' to the 'nginx' group
sudo usermod -a -G nginx root
sudo usermod -a -G nginx www-data
sudo usermod -a -G nginx jenkins

# Change the group ownership of the project directory and its contents to 'nginx'

sudo chown root:nginx /var/lib/jenkins/workspace/FARMS
sudo chown -R root:nginx /var/lib/jenkins/workspace/FARMS

sudo chown -R root:nginx /var/lib/jenkins/workspace/FARMS/staticfiles
sudo chown -R root:nginx /var/lib/jenkins/workspace/FARMS/app
sudo chown -R root:nginx /var/lib/jenkins/workspace/FARMS/FARMS

sudo chmod 770 /var/lib/jenkins/workspace/FARMS
sudo chmod 770 -R /var/lib/jenkins/workspace/FARMS/staticfiles