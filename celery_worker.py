# -*- coding: utf-8 -*-
from celery import Celery

from app import create_app
from config import running_config

celery_app = Celery("backend_celery", broker="redis://127.0.0.1:6379/1")
celery_app.config_from_object(running_config)

# Initial the flask app to have mail and sqlchemy initialization for celery process
# If there will be no mail or sql operation for background task, there is no need to create
# a flash app.
flask_app = create_app(running_config)
