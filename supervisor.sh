#!/bin/bash

source env/bin/activate

# Set environment variables here
export ENV_PATH=".env.prod"

cd /var/lib/jenkins/workspace/FARMS/

python3 manage.py migrate
echo "Migrations done"
python3 manage.py collectstatic --noinput
echo "collectstatic done"

# giving permission to static files
sudo chmod 770 -R /var/lib/jenkins/workspace/FARMS/staticfiles

cd /var/lib/jenkins/workspace/FARMS

# Delete the old Supervisor configuration file, if it exists
sudo rm -f /etc/supervisor/conf.d/FARMS_SUPERVISOR.conf

# Copy the new Supervisor configuration file
sudo cp FARMS_SUPERVISOR.conf /etc/supervisor/conf.d/FARMS_SUPERVISOR.conf

echo "$USER"
echo "$PWD"

# Reload Supervisor configurations
sudo supervisorctl reread
sudo supervisorctl update

sudo systemctl daemon-reload

# Check the status of the gunicorn process
status=$(sudo supervisorctl -c /etc/supervisor/supervisord.conf status farms_gunicorn | awk '{print $2}')

# If gunicorn is running, restart it; otherwise, start it
if [ "$status" = "RUNNING" ]; then
    echo "Gunicorn is running. Restarting..."
    sudo supervisorctl -c /etc/supervisor/supervisord.conf restart farms_gunicorn
else
    echo "Gunicorn is not running. Starting..."
    sudo supervisorctl -c /etc/supervisor/supervisord.conf start farms_gunicorn
fi

# Check the status of the celery_worker process
status=$(sudo supervisorctl -c /etc/supervisor/supervisord.conf status farms_celery_worker | awk '{print $2}')

# If celery_worker is running, restart it; otherwise, start it
if [ "$status" = "RUNNING" ]; then
    echo "celery_worker is running. Restarting..."
    sudo supervisorctl -c /etc/supervisor/supervisord.conf restart farms_celery_worker
else
    echo "celery_worker is not running. Starting..."
    sudo supervisorctl -c /etc/supervisor/supervisord.conf start farms_celery_worker
fi

#sudo supervisorctl start gunicorn
#echo "Gunicorn restarted."
#sudo supervisorctl start celery_worker
#echo "Celery Worker restarted."

sudo supervisorctl status farms_gunicorn
sudo supervisorctl status farms_celery_worker