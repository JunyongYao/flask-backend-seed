# -*- coding: utf-8 -*-

import logging

from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_restful_swagger import swagger

db = SQLAlchemy()
mail = Mail()
redis = FlaskRedis()


def create_app(active_config):
    flask_app = Flask(__name__)
    CORS(flask_app)
    logging.info("Use config {}".format(active_config.name))

    flask_app.config.from_object(active_config)
    flask_app.secret_key = flask_app.config["SECRET_KEY"]

    if flask_app.config["REVERSE_PROXY"]:
        from werkzeug.contrib.fixers import ProxyFix
        logging.info("Fix reverse proxy issue!")
        flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app)

    mail.init_app(flask_app)
    # flask_app.app_context().push()

    redis.init_app(flask_app)
    logging.info("Use redis server {}".format(flask_app.config["REDIS_URL"]))
    logging.debug("redis is {}".format(redis.ping()))
    if not redis.ping():
        logging.error("Cannot initialize redis with result {}!".format(redis.ping()))
        return None

    logging.info("Use DB {}".format(flask_app.config["SQLALCHEMY_DATABASE_URI"]))
    db.init_app(flask_app)
    # the Flask-SQLAlchemy needs current app to run
    with flask_app.app_context():
        db.create_all()

    return flask_app


def add_api_support(flask_app):
    api = Api(flask_app)
    api = swagger.docs(api, apiVersion="0.1", produces=["application/json", "text/html"], api_spec_url='/api/spec',
                       description='A Sample for API list')

    add_restapi_endpoints(api)

    logging.debug("Added rest api entries")

    return flask_app


def add_restapi_endpoints(api):
    prefix = "/api/sample"
    from app.restApi.loginApi import LoginDataProvider
    api.add_resource(LoginDataProvider, "{}/login".format(prefix))

    from app.restApi.userApi import UserInfoProvider, BackgroundTaskProvider
    api.add_resource(UserInfoProvider, "{}/user_info".format(prefix))
    api.add_resource(BackgroundTaskProvider, "{}/task".format(prefix))

