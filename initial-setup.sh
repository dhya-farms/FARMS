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
sudo apt-get install -y gcc libpq-dev make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git python3 python3-dev libxml2-dev libxslt1-dev zlib1g-dev python3-pip python3-venv python3-wheel

# install nginx and supervisor
sudo apt-get install nginx supervisor

sudo systemctl daemon-reload
sudo systemctl start nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
sudo systemctl status nginx


sudo systemctl start supervisor
sudo systemctl restart nginx
sudo systemctl enable supervisor
sudo systemctl status supervisor
