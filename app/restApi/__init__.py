# -*- coding: utf-8 -*-
import functools
import logging
import sys
import traceback
from flask import make_response, current_app, jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import get_debug_queries

from app import db
from app.cache.userCache import UserInfoCache
from app.swagger.contants import ERR_MSG_INVALID_TOKEN, ERR_MSG_INVALID_PERMISSION, ERR_INVALID_SIGH
from app.util.common import get_dict_sign


def handle_db_exception_inner(func):
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


def login_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        perm_parser = reqparse.RequestParser()
        perm_parser.add_argument("Token", type=str, required=True, location="headers")
        got_args = perm_parser.parse_args(strict=False)

        cur_user_id = UserInfoCache.UserToken.get(got_args["Token"])
        if cur_user_id is None:
            return make_response(jsonify(ERR_MSG_INVALID_TOKEN), 400)

        # FIXME: It is ugly because it assumes login_required will be used with ProtectedResource
        func.__self__.USER_ID = cur_user_id
        return func(*args, **kwargs)

    return inner


def query_authorized(func):
    """
    Signing the query parameters sorted in lower-case, alphabetical order using the private credential as the signing
    token.
    Signing should occur before URL encoding the query string.
    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        # only check the query string
        logging.info("url is {} for method {}".format(request.url_rule, request.method))

        valid_query_param_dict = {}
        found_sign_val = None
        for key, value in request.args.items():
            logging.info("Arg is {}:{}".format(key, value))
            if str(key).lower() != "signature":
                valid_query_param_dict[key] = value
            else:
                found_sign_val = value

        if not found_sign_val:
            return make_response(jsonify(ERR_INVALID_SIGH), 400)

        compute_val = get_dict_sign(request.url_rule, valid_query_param_dict)
        if compute_val != found_sign_val:
            return make_response(jsonify(ERR_INVALID_SIGH), 400)

        return func(*args, **kwargs)

    return inner


def permission_validate(*permission_class_list):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            http_parser = reqparse.RequestParser()
            http_parser.add_argument("Token", type=str, required=True, location="headers")
            http_parser.add_argument("storeCode", type=int)
            http_args = http_parser.parse_args(strict=False)

            cur_user_id = UserInfoCache.UserToken.get(http_args["Token"])
            if cur_user_id is None:
                return make_response(jsonify(ERR_MSG_INVALID_TOKEN), 400)

            for permission_class in permission_class_list:
                if not permission_class.validate(cur_user_id):
                    return make_response(jsonify(ERR_MSG_INVALID_PERMISSION), 400)

            return func(*args, **kwargs)

        return inner

    return wrapper


class TokenAuthenticatedResource(Resource):
    """
    The resource will use Token inside header to ensure than only valid user can call APIs.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.USER_ID = None

    # Be careful for the order in this decorator list. The previous one will be the inner one in the decorate chain.
    method_decorators = [login_required, handle_db_exception_inner]


class SignAuthorizedResource(Resource):
    """
    The resource will use sign in query to ensure the request will be called by authorized client.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Be careful for the order in this decorator list. The previous one will be the inner one in the decorate chain.
    method_decorators = [query_authorized, handle_db_exception_inner]
