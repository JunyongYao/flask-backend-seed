# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse
from flask_restful_swagger import swagger
from flask import make_response, jsonify

from app.model.userModel import UserInfo
from app.restApi import handle_db_exception_inner
from app.swagger.models import get_token_info, TokenInfo


class LoginDataProvider(Resource):
    """ Login user with name and password and get its token for further operations. """
    @swagger.operation(
        notes="Provided user name and password for login process. ",
        responseClass=TokenInfo.__name__,
        parameters=[
            {
                "name": "name",
                "description": "blueprint object that needs to be added. YAML.",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "form"
            },
            {
                "name": "pwd",
                "description": "password!",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "form"
            }
        ],
        responseMessages=[
            {
                "code": 400,
                "message": "Cannot find register user via provided info"
            }
        ]
    )
    @handle_db_exception_inner
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
            return make_response(jsonify(get_token_info(match_user)), 200)
        else:
            result = {"error": "INVALID_USER", "message": "Cannot find register user via provided info"}
            return make_response(jsonify(result), 400)
