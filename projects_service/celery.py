import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projects_service.settings.prod")

app = Celery("projects_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
