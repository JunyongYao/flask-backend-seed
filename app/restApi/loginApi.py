# -*- coding: utf-8 -*-
import time

from flask_restful import Resource, reqparse
from flask import make_response, jsonify

from app.model.userModel import UserInfo
from app.restApi import handle_db_exception


class LoginDataProvider(Resource):
    @handle_db_exception()
    def post(self):
        parser_args = reqparse.RequestParser()
        parser_args.add_argument("name", type=str, required=True)
        parser_args.add_argument("pwd", type=str, required=True)
        args = parser_args.parse_args()

        match_user = UserInfo.query.filter(
            UserInfo.name == args["name"],
            UserInfo.sha_pwd == UserInfo.generate_sha_pwd(args["pwd"])
        ).first()

        if match_user:
            # give new token back
            expire_length_sec = 3600 * 24  # The valid token is 1 day long
            result = {"token": match_user.generate_auth_token(expire_length_sec),
                      "expire_at": int((time.time() + expire_length_sec) * 1000)}

            return make_response(jsonify(result), 200)
        else:
            result = {"error": "INVALID_USER", "message": "Cannot find register user via provided info"}
            return make_response(jsonify(result), 400)
