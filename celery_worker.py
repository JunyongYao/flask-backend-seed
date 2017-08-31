# -*- coding: utf-8 -*-
import os
import sys
from celery import Celery
from celery.schedules import crontab

from app import create_app
from config import running_config, basedir


# Initial the flask app to have mail and sqlchemy initialization for celery process
# If there will be no mail or sql operation for background task, there is no need to create
# a flash app.
flask_app = create_app(running_config)


def make_celery(app):
    celery = Celery("backend_celery", broker=flask_app.config["CELERY_BROKER_URL"])
    celery.conf.update(flask_app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

celery_app = make_celery(flask_app)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print("celery setup_periodic_tasks initialized")
    async_task_module_path = os.path.join(basedir, "task")
    sys.path.append(basedir)
    sys.path.append(async_task_module_path)

    """
    # Here is a sample for running celery beat for regular task. For more details, you can refer 
    #  http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
    # And it is highly recommended to use Jenkins for regular task trigger and monitor. Because it has a lot of plugin 
    #  support with better stability and flexibility.
    
    
    from task.asyncTask import sync_test
    sender.add_periodic_task(10.0, sync_test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, sync_test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=16, minute=48),
        sync_test.s('Happy Mondays!'),
    )
    """
