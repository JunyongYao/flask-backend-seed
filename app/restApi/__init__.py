# -*- coding: utf-8 -*-
import functools
import logging
import sys
import traceback
from flask import make_response, current_app
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import get_debug_queries

from app import db


def handle_db_exception():
    def func_track(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                result = func(*args, **kw)
                # record the slow sql execution
                for query in get_debug_queries():
                    if query.duration >= current_app.config['FLASK_SLOW_DB_QUERY_TIMEOUT']:
                        logging.warning('Slow query: {}\nParameters: {}\nDuration: {} seconds\nContext: {}\n'.format(
                            query.statement, query.parameters, query.duration, query.context))
            except SQLAlchemyError:
                logging.exception("Exception found in {}".format(func.__name__))
                subject = "Exception found in {}".format(func.__name__)
                db.session.rollback()
                # get the exception logs
                body = str("\n".join(traceback.format_tb(sys.exc_info()[2])))
                from app.util.common import send_mail
                send_mail(subject, body)

                result = make_response("SQL Error", 500)
            finally:
                db.session.remove()

            return result

        return wrapper

    return func_track

