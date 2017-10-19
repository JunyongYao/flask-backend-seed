# -*- coding: utf-8 -*-
import logging
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

