# -*- coding: utf-8 -*-
import logging

from app.cache.basic import DictCacheABC, DataCacheABC
from app.model.userModel import UserInfo


class UserInfoCache(object):
    class UserToken(DataCacheABC):
        def __init__(self, token):
            super().__init__()
            self.token = token

        @property
        def cache_key(self):
            return "CACHE_UserInfoCache_Token_{}".format(self.token)
            pass

        def data_retrieve_ops(self):
            user_info = UserInfo.verify_auth_token(self.token)
            if user_info is None:
                return None

            return user_info.id

        @property
        def expire_in_seconds(self):
            return 10 * 60

    class UserProfile(DictCacheABC):
        def __init__(self, user_id):
            super().__init__()
            self.user_id = user_id
            # if this is set, it will auto refresh token if user access this value under threshold time
            self.auto_refresh_threshold = 3 * 60

        @property
        def cache_key(self):
            return "CACHE_UserInfoCache_UserProfile_{}".format(self.user_id)

        @property
        def expire_in_seconds(self):
            return 30 * 60

        def data_retrieve_ops(self):
            user_info = UserInfo.get_user(self.user_id)
            return user_info.to_json()

