#!/bin/sh
set -e

gunicorn -b :80 --chdir ./FARMS.wsgi:application