# -*- coding: utf-8 -*-
import time
from flask_restful import fields
from flask_restful_swagger import swagger

"""
Use the file to define all return structure can ensure the return data is aligned with swagger document.
For complicated return structure, need to use swagger.nested for definition.
"""


@swagger.model
class TokenInfo:
    resource_fields = {
        "token": fields.String,
        "expire_at": fields.Integer,
    }
    required = ["token", "expire_at"]
    swagger_metadata = {
        "token": {"description": "The token user can used for further restful api authentication"},
        "expire_at": {"description": "The miliseconds when this token will be expired"}
    }


def get_token_info(user_info):
    expire_length_sec = 3600 * 24  # The valid token is 1 day long
    return {"token": user_info.generate_auth_token(expire_length_sec),
            "expire_at": int((time.time() + expire_length_sec) * 1000)}
