# -*- coding: utf-8 -*-

COMMON_SUCCESS = {"error": "OK", "message": "OK"}

ERR_MSG_INVALID_TOKEN = {
    "error": "INVALID_TOKEN",
    "message": "Token is expired or invalid, please try to get a new one"
}

ERR_MSG_INVALID_PERMISSION = {
    "error": "INVALID_PERMISSION",
    "message": "No permission!"
}

ERR_NO_DATA = {
    "error": "ERROR_NO_DATA",
    "message": "Data do not exists."
}

ERR_INVALID_DATE_STR = {
    "error": "INVALID_DATE_STR",
    "message": "Illegal date format or value provided."
}

ERR_INVALID_SIGH = {
    "error": "ERR_INVALID_SIGH",
    "message": "Provided sign cannot match given data inside query"
}


def get_dict_message(error_dict):
    return "{}: {}".format(error_dict["error"], error_dict["message"])
