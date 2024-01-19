#!/bin/bash

NAME="FARMS"
DJANGODIR=/var/lib/jenkins/workspace/FARMS
USER=root
GROUP=root
NUM_WORKERS=5
DJANGO_SETTINGS_MODULE=FARMS.settings
DJANGO_WSGI_MODULE=FARMS.wsgi
SOCKFILE=/tmp/gunicorn_farms.sock
ACCESS_LOG=${DJANGODIR}/logs/django_server_stdout.log
ERROR_LOG=${DJANGODIR}/logs/django_server_stderr.log

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
source ${DJANGODIR}/env/bin/activate

# Export the settings module for Django
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start Gunicorn
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --worker-class gevent \
  --bind unix:$SOCKFILE \
  --log-level info \
  --access-logfile $ACCESS_LOG \
  --error-logfile $ERROR_LOG \
  --timeout 300