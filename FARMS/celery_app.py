from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FARMS.settings")
app = Celery("app")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_transport_options = {'visibility_timeout': 21600}  # Taken from lokalads

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
