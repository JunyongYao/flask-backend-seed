# -*- coding: utf-8 -*-
import os
import logging
import yaml
from logging import NullHandler

basedir = os.path.abspath(os.path.dirname(__file__))
logging.getLogger(__name__).addHandler(NullHandler())


def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    default_yaml = os.getenv(env_key, default_path)
    if os.path.exists(default_yaml):
        with open(default_yaml, 'rt') as f:
            log_config = yaml.safe_load(f.read())
            root_log_dir = os.path.join(basedir, "logs")

            if not os.path.exists(root_log_dir):
                os.mkdir(root_log_dir)

            log_config["handlers"]["info_file_handler"]["filename"] = os.path.join(root_log_dir,
                                                                                   log_config["handlers"][
                                                                                       "info_file_handler"]["filename"])
            log_config["handlers"]["error_file_handler"]["filename"] = os.path.join(root_log_dir,
                                                                                    log_config["handlers"][
                                                                                        "error_file_handler"][
                                                                                        "filename"])
            from logging.config import dictConfig
            dictConfig(log_config)
    else:
        logging.basicConfig(level=default_level)

    logging.info("Logger is initialized")


# Only the UpperCase config can be active
class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or r"xkb\xe4\x06\x83\xa9\xd1,=\x85\xa9w\xda'\xcc\x12\x1a\x84\xd71}\xab\x1b"

    # MYSQL Server configuration
    MYSQL_DATABASE_CHARSET = "utf8mb4"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # performance record
    SQLALCHEMY_RECORD_QUERIES = True
    FLASK_SLOW_DB_QUERY_TIMEOUT = 0.5

    # email server
    MAIL_SERVER = 'smtp.ym.163.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # TODO: the receiver mail for alert, please fill in your account
    # default recipient
    RECIPIENTS = ['receiver_A@XXXXX.com', 'receiver_B@XXXXX.com']
    SENDER = "monitor@XXXX.com"

    # for redis cache
    REDIS_URL = "redis://127.0.0.1:6379/0"

    # for celery
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json', 'pickle']
    CELERY_BROKER_URL = "redis://127.0.0.1:6379/1"
    CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/1"
    CELERY_TIMEZONE = "UTC+08:00"
    # If the result should be handled, this value must be False
    CELERY_IGNORE_RESULT = True
    # If the timeout should exceeds this value, need to update the global setting and use task specific one
    CELERYD_TASK_SOFT_TIME_LIMIT = 900
    CELERYD_TASK_TIME_LIMIT = 1800
    # TODO: need to update if new async task should be imported
    CELERY_IMPORTS = ("task.asyncTask", )
    # this is one week length to align with business logic.
    # celery will redeliver task to another and there might be multiple execution
    #  http://docs.celeryproject.org/en/latest/getting-started/brokers/redis.html#redis-visibility-timeout
    BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 604800}


class DevelopmentConfig(Config):
    name = "DevelopmentConfig"
    DEBUG = True
    REVERSE_PROXY = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

    # email server
    MAIL_SERVER = 'smtp.ym.163.com'
    MAIL_USERNAME = "monitor@XXXX.com"
    MAIL_PASSWORD = "monitor_password"

    SENDER = "monitor@XXXX.com"


class TestingConfig(Config):
    name = "TestingConfig"
    DEBUG = True
    REVERSE_PROXY = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):
    name = "ProductionConfig"
    DEBUG = False
    REVERSE_PROXY = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

conf_name = os.getenv("RUN_CONFIG") or 'testing'
running_config = config[conf_name]
