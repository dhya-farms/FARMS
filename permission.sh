# Create a new group called 'nginx'
sudo groupadd jenkins

# Add 'www-data', 'root', and 'www-data' to the 'jenkins' group
sudo usermod -a -G jenkins root
sudo usermod -a -G jenkins www-data

# Change the group ownership of the project directory and its contents to 'nginx'

sudo chmod 775 /var/lib/jenkins/workspace/FARMS
sudo chmod 775 -R /var/lib/jenkins/workspace/FARMS/
sudo chmod 770 -R /var/lib/jenkins/workspace/FARMS/app
#sudo chmod 770 -R /var/lib/jenkins/workspace/FARMS/staticfiles