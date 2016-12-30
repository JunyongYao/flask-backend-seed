# -*- coding: utf-8 -*-

import functools
import logging
import traceback
import sys


def only_one(function=None, key="", timeout=None):
    """Enforce only one celery task at a time."""

    def _dec(run_func):
        """Decorator."""

        def _caller(*args, **kwargs):
            """Caller."""
            ret_value = None
            have_lock = False
            from app import redis
            lock = redis.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    ret_value = run_func(*args, **kwargs)
            finally:
                if have_lock:
                    lock.release()

            return ret_value

        return _caller

    return _dec(function) if function is not None else _dec


def send_mail_if_fail(expect_val=None):
    """
    It only support following return type:
        single variable, tuple, array

    Warning:
        don't expect it can compare the object by default, python use id() as default comparison.
        if you want to do it,
        override the __cmp__ or __eq__ in the object's class at first.

    :param expect_val:
        default is None, it means it will not check the return value and only catch exception during runtime.
        if it is set, it will only check the first item in tuple or array.
        E.G.
            True    expect_val=True
            (True, "****") expect_val=True
            [abc, '***', '*****']
    """

    def func_track(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            result = func(*args, **kw)
            same_result = True
            if expect_val is not None:
                if isinstance(result, list) or isinstance(result, tuple):
                    same_result = result[0] == expect_val
                else:
                    same_result = result == expect_val

            if not same_result:
                subject = "Return value is not expected"
                body = "{} returned {} but {} was expected".format(func.__name__, str(result), str(expect_val))
                from app.util.common import send_mail
                send_mail(subject, body)
                logging.warning(body)

            return result

        return wrapper

    return func_track


def handle_and_send_mail_for_exception(default_value):
    def func_track(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                result = func(*args, **kw)
            except Exception as e:
                logging.error("Exception found in {}".format(func.__name__))
                logging.exception(e)
                subject = "Exception found in {}".format(func.__name__)
                # get the exception logs
                body = str("\n".join(traceback.format_tb(sys.exc_info()[2])))
                from app.util.common import send_mail
                send_mail(subject, body)
                logging.warning(body)
                result = default_value

            return result

        return wrapper

    return func_track
