# -*- coding: utf-8 -*-

import time

import logging

import pickle
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


@celery_app.task(soft_time_limit=10, time_limit=20)
def send_async_email(title, body):
    logger.debug("Send async mail with title {} and body {}".format(title, body))
    send_mail(title, body)


@celery_app.task(bind=True, max_retries=3)
def send_async_info_with_retry(self, info):
    """
    You can use redis.lock to protect isolation operation from paralleled running. Here is a sample:

    # import required library
    from app import redis
    # initialize the lock
    my_lock = redis.lock("send_wechat_template_for_task_statistic_{}".format(push_id))

    # For maintain, don't using blocking=True if you're 100% sure there is not dead lock under any condition
    if my_lock.acquire(blocking=False):
        try:
            from app.util.notification import send_notification_for_task_statistic
            cnt = send_notification_for_task_statistic(push_id)
            logger.info("Send notification to {} users".format(cnt))
        except Exception as exc:
            logger.warning("Has Exception {}".format(str(exc)))
            self.retry(exc=exc, countdown=10)
            return
        finally:
            # need to release the lock in the first line of finally block
            my_lock.release()
    else:
        logger.warning("send_wechat_template_for_task_statistic got lock for {}".format(push_id))
        send_sync_email("send_wechat_template_for_task_statistic got lock", "push id is {}, please check!".format(push_id))
    """
    try:
        time.sleep(10)
        logger.info("Got user's input {}".format(info))
    except Exception as exc:
        logger.warning("Has Exception {}".format(str(exc)))
        self.retry(exc=exc, countdown=10)


@celery_app.task(soft_time_limit=30, time_limit=60)
def sync_test(arg):
    logging.info("Got args from caller {}".format(arg))


@celery_app.task(soft_time_limit=120, time_limit=240)
def refresh_cache(pickle_obj):
    """
    It uses pickle_obj to refresh the cache. This is a lower priority task. Therefore, no retry will be triggered if
    there is failure.
    One known issue is, there might be 'OperationalError, 2013' error during query database.
    This solution supports distributed task queue. And it sacrifices security to get better re-use and neat code.
    """
    run_obj = pickle.loads(pickle_obj)
    logging.info("Refresh for key {}".format(run_obj.cache_key))
    run_obj.refresh()
