import time

from celery.utils.log import get_task_logger
from celery.signals import task_postrun

from celery_worker import celery_app
from app.util.common import send_mail
from app import db

logger = get_task_logger(__name__)


@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors
    # won't propagate across tasks)
    db.session.remove()


@celery_app.task
def send_async_email(title, body):
    logger.debug("Send async mail with title {} and body {}".format(title, body))
    send_mail(title, body)


@celery_app.task(bind=True, max_retries=3)
def send_async_info_with_retry(self, info):
    """
    You can use redis.lock to protect isolation operation from paralleled running
    """
    try:
        time.sleep(10)
        logger.info("Got user's input {}".format(info))
    except Exception as exc:
        logger.warning("Has Exception {}".format(str(exc)))
        self.retry(exc=exc, countdown=10)
