sudo apt update
sudo apt install fontconfig openjdk-17-jre
java -version

sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins

sudo systemctl daemon-reload
sudo systemctl start jenkins
sudo systemctl restart jenkins
sudo systemctl enable jenkins
sudo systemctl status jenkins

# OS dependencies
sudo apt-get install software-properties-common
sudo apt-add-repository universe
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y gcc libpq-dev make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git python3 python-dev python3-dev libxml2-dev libxslt1-dev zlib1g-dev python-pip libmysqlclient-dev gcc libpq-dev python-dev python-pip python-wheel python3-dev python3-pip python3-venv python3-wheel

# install nginx and supervisor
sudo apt-get install nginx supervisor

# Function to start or restart a service
start_or_restart_service() {
    local service_name=$1

    # Check if the service is active
    if systemctl is-active --quiet $service_name; then
        echo "$service_name is running. Restarting..."
        sudo systemctl restart $service_name
    else
        echo "$service_name is not running. Starting..."
        sudo systemctl start $service_name
    fi

    # Enable the service to start on boot
    sudo systemctl enable $service_name

    # Display the status of the service
    sudo systemctl status $service_name
}

# Reload the systemd daemon
sudo systemctl daemon-reload

# Manage nginx service
start_or_restart_service nginx

# Manage supervisor service
start_or_restart_service supervisor