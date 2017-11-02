# -*- coding: utf-8 -*-
import collections
import logging
from hashlib import sha256
from flask_mail import Message
from flask import current_app


def send_mail(title, body, html=None, receiver_list=None):
    if current_app.config["MAIL_USERNAME"] is None:
        logging.error("Mail is not configured correctly!")
        return

    if current_app.config["DEBUG"]:
        title = "TEST SERVER:" + title

    if receiver_list:
        recipients = receiver_list
    else:
        recipients = current_app.config["RECIPIENTS"]

    msg = Message(title, sender=current_app.config["SENDER"], recipients=recipients, body=body, html=html)

    from app import mail
    with current_app.app_context():
        mail.send(msg)

    logging.info("Send mail finished!")


def get_dict_sign(uri, dict_data: dict) -> str:
    # refer https://stackoverflow.com/questions/319530/restful-authentication/7158864#7158864 for implementation
    # sign something like "/object?apikey=Qwerty2010&timestamp=1261496500"
    order_dict = collections.OrderedDict(sorted(dict_data.items()))
    encrypt_str = str(uri) if str(uri).startswith("/") else "/" + str(uri)
    #  Signing the query parameters sorted in lower-case, alphabetical order using the private credential as the signing
    #   token.
    value_list = []
    for key, value in order_dict.items():
        value_list.append("{}={}".format(str(key).lower(), value))

    encrypt_str += "?" + "&".join(value_list) + current_app.config["SIGN_KEY"]

    sign_256 = sha256()
    sign_256.update(encrypt_str.encode("utf-8"))

    return sign_256.hexdigest()
