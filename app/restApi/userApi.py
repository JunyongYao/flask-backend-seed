# -*- coding: utf-8 -*-
import logging

from flask import make_response, jsonify
from flask_restful import Resource, reqparse

from app import db
from app.cache.userCache import UserInfoCache
from app.model.userModel import UserInfo
from app.permission import permissions
from app.restApi import ProtectedResource, handle_db_exception_inner, permission_validate
from task.asyncTask import send_async_info_with_retry, send_async_email


# This class uses ProtectedResource which will ensure user's token is valid
class UserInfoProvider(ProtectedResource):
    # Sample to set permission for interface.
    @permission_validate(permissions.AlwaysPass)
    def get(self):
        result = UserInfoCache.UserProfile.get(self.USER_ID)

        return make_response(jsonify(result), 200)

    def put(self):
        base_parser = reqparse.RequestParser()
        base_parser.add_argument("NewName", type=str, required=True)
        args = base_parser.parse_args(strict=True)

        cur_user = UserInfo.get_user(self.USER_ID)
        cur_user.nickname = args["NewName"]
        db.session.commit()

        # clear the expired cache
        UserInfoCache.UserProfile.clear(self.USER_ID)

        return make_response("OK", 200)


class BackgroundTaskProvider(Resource):
    """
    This sample class uses Resource as base class means it has no login required.
    """
    @handle_db_exception_inner
    def get(self):
        # do some background task soon
        logging.debug("This task will be executed in the background soon")
        send_async_info_with_retry.delay("This is for backend running!")

        # do some background task after 15 seconds
        logging.debug("This task will be pushed to celery and executed after 15 seconds")
        send_async_email.apply_async(args=["mail title", "mail body"], countdown=15)

        return make_response("OK", 200)
