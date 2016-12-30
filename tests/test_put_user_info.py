# -*- coding: utf-8 -*-

from tests.test_basics import BasicsTestCase
from app import db


class UserInfoTest(BasicsTestCase):
    def test_put_user_name(self):
        user_name = "NewUser"
        user_pwd = "UserPwd"

        db_user = self.create_test_user(user_name, user_pwd)
        old_nickname = db_user.nickname
        new_nickname = self.generate_random_string(10)

        # this is necessary for test case to avoid impact function code's sqlalchemy session
        db.session.remove()

        # get the user token
        login_data = {
            "name": user_name,
            "pwd": user_pwd
        }
        code, json_msg = self.post_login(data=login_data)
        self.assertEqual(200, code, json_msg)

        user_header = {
            "Token": json_msg["token"]
        }

        # check the old nick name
        code, json_msg = self.get_user_info(header=user_header)
        self.assertEqual(200, code, json_msg)
        self.assertTrue("name" in json_msg, json_msg)
        self.assertTrue("gender" in json_msg, json_msg)
        self.assertTrue("city" in json_msg, json_msg)
        self.assertEqual(json_msg["name"], old_nickname, json_msg)

        # use token to update user info
        code, json_msg = self.put_user_info(data={"NewName": new_nickname}, header=user_header)
        self.assertEqual(200, code, json_msg)

        # get the new user info from db
        code, json_msg = self.get_user_info(header=user_header)
        self.assertEqual(200, code, json_msg)
        self.assertEqual(json_msg["name"], new_nickname, json_msg)
