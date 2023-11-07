#!/bin/bash

source env/bin/activate

cd /var/lib/jenkins/workspace/FARMS/

python3 manage.py migrate
echo "Migrations done"
python3 manage.py collectstatic --noinput
echo "collectstatic done"

cd /var/lib/jenkins/workspace/FARMS

sudo cp -rf gunicorn.socket /etc/systemd/system/
sudo cp -rf gunicorn.service /etc/systemd/system/

echo "$USER"
echo "$PWD"



sudo systemctl daemon-reload
sudo systemctl start gunicorn

echo "Gunicorn has started."

sudo systemctl enable gunicorn

echo "Gunicorn has been enabled."

sudo systemctl restart gunicorn


sudo systemctl status gunicorn
