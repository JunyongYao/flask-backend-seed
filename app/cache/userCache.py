# -*- coding: utf-8 -*-
import logging

from app.model.userModel import UserInfo
from app.cache import get_redis_dict, set_redis_dict_with_timeout, get_redis_data, set_redis_data_with_timeout
from app import redis


class UserInfoCache(object):
    @staticmethod
    def verify_auth_token(token: str) -> int:
        cache_key = "CACHE_UserInfoCache_Token_{}".format(token)
        expire_in_seconds = 10 * 60
        cache_user_id = get_redis_data(cache_key)

        if cache_user_id is None:
            user_info = UserInfo.verify_auth_token(token)
            if user_info is None:
                return None

            cache_user_id = user_info.id
            set_redis_data_with_timeout(cache_key, cache_user_id, expire_in_seconds)
            logging.debug("Store token for {} which will expire after {} seconds".format(cache_key, expire_in_seconds))
        else:
            expire_in_seconds = redis.ttl(cache_key)
            logging.debug("Use stored token data for user will expire after {} seconds".format(expire_in_seconds))

        return cache_user_id

    class UserProfile(object):
        key_pattern = "CACHE_UserInfoCache_UserProfile_{}"
        expire_in_seconds = 10 * 60

        @classmethod
        def get(cls, user_id: int) -> dict:
            cache_key = cls.key_pattern.format(user_id)
            data = get_redis_dict(cache_key)

            if data is None:
                user_info = UserInfo.get_user(user_id)
                data = user_info.to_json()

                set_redis_dict_with_timeout(cache_key, data, cls.expire_in_seconds)
                logging.debug("Store user profile for {} which will expire after {} seconds".format(
                    cache_key, cls.expire_in_seconds))
            else:
                expire_in_seconds = redis.ttl(cache_key)
                logging.debug("Use stored user profile will expire after {} seconds".format(expire_in_seconds))

            return data

        @classmethod
        def clear(cls, user_id):
            cache_key = cls.key_pattern.format(user_id)
            redis.delete(cache_key)
