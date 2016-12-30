# -*- coding: utf-8 -*-
import json
import random
import string
import unittest

from flask import current_app
from config import config
from app import create_app, db, redis, add_api_support


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        test_app = create_app(config['testing'])
        test_app = add_api_support(test_app)
        self.assertTrue(current_app.config['TESTING'])

        self.app_context = test_app.app_context()
        self.app_context.push()

        self.test_client = test_app.test_client()
        db.drop_all()
        db.create_all()
        redis.flushall()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    @staticmethod
    def _parse_result(res_data):
        data = str(res_data, "utf-8")
        try:
            ret_data = json.loads(data)
        except ValueError:
            ret_data = data

        return ret_data

    @staticmethod
    def generate_random_string(length):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(length))

    def create_test_user(self, name, pwd):
        from app.model.userModel import UserInfo
        stored_pwd = UserInfo.generate_sha_pwd(pwd)
        new_user = UserInfo(name=name,
                            sha_pwd=stored_pwd,
                            nickname=self.generate_random_string(5))
        db.session.add(new_user)
        db.session.commit()

        return new_user

    def get_request(self, url, data=None, header=None):
        response = self.test_client.get(url, data=data, headers=header)
        return response.status_code, self._parse_result(response.data)

    def put_request(self, url, data=None, header=None):
        response = self.test_client.put(url, data=data, headers=header)
        return response.status_code, self._parse_result(response.data)

    def post_request(self, url, data=None, header=None):
        response = self.test_client.post(url, data=data, headers=header)
        return response.status_code, self._parse_result(response.data)

    def delete_request(self, url, data=None, header=None):
        response = self.test_client.delete(url, data=data, headers=header)
        return response.status_code, self._parse_result(response.data)

    def post_login(self, data):
        url = "/api/sample/login"
        return self.post_request(url, data=data)

    def get_user_info(self, header):
        url = "/api/sample/user_info"
        return self.get_request(url, header=header)

    def put_user_info(self, data, header):
        url = "/api/sample/user_info"
        return self.put_request(url, data=data, header=header)
