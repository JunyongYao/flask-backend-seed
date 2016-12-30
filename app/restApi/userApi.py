# -*- coding: utf-8 -*-
import logging

from flask import make_response, jsonify
from flask_restful import Resource, reqparse

from app import db
from app.cache.userCache import UserInfoCache
from app.model.userModel import UserInfo
from app.restApi import handle_db_exception
from task.asyncTask import send_async_info_with_retry, send_async_email


class UserInfoProvider(Resource):
    @handle_db_exception()
    def get(self):
        base_parser = reqparse.RequestParser()
        base_parser.add_argument("Token", type=str, required=True, location="headers")
        args = base_parser.parse_args(strict=True)

        cur_user_id = UserInfoCache.verify_auth_token(args["Token"])
        if cur_user_id is None:
            result = {"error": "INVALID_TOKEN", "message": "Invalid TOKEN"}
            return make_response(jsonify(result), 400)

        result = UserInfoCache.UserProfile.get(cur_user_id)

        return make_response(jsonify(result), 200)

    @handle_db_exception()
    def put(self):
        base_parser = reqparse.RequestParser()
        base_parser.add_argument("Token", type=str, required=True, location="headers")
        base_parser.add_argument("NewName", type=str, required=True)
        args = base_parser.parse_args(strict=True)

        cur_user_id = UserInfoCache.verify_auth_token(args["Token"])
        if cur_user_id is None:
            result = {"error": "INVALID_TOKEN", "message": "Invalid TOKEN"}
            return make_response(jsonify(result), 400)

        cur_user = UserInfo.get_user(cur_user_id)
        cur_user.nickname = args["NewName"]
        db.session.commit()

        # clear the expired cache
        UserInfoCache.UserProfile.clear(cur_user_id)

        return make_response("OK", 200)


class BackgroundTaskProvider(Resource):
    @handle_db_exception()
    def get(self):
        # do some background task soon
        logging.debug("This task will be executed in the background soon")
        send_async_info_with_retry.delay("This is for backend running!")

        # do some background task after 15 seconds
        logging.debug("This task will be pushed to celery and executed after 15 seconds")
        send_async_email.apply_async(args=["mail title", "mail body"], countdown=15)

        return make_response("OK", 200)
