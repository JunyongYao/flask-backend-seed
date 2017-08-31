# -*- coding: utf-8 -*-
import json

import logging

from app import redis


def set_redis_dict(key, data):
    data_str = json.dumps(data)
    redis.set(key, data_str)


def get_redis_data(key):
    data = redis.get(key)
    if data:
        data = data.decode('utf-8')

    return data


def get_redis_dict(key):
    data_str = get_redis_data(key)
    if data_str:
        return json.loads(data_str)

    return None


def set_redis_dict_with_timeout(key, value, time_out):
    set_redis_dict(key, value)
    redis.expire(key, time_out)


def set_redis_data_with_timeout(key, value, time_out):
    redis.set(key, value)
    redis.expire(key, time_out)


def set_data_if_key_expire(key, ttl, set_func):
    data = get_redis_data(key)

    if data is None:
        data = set_func()
        # only set data which is not None
        if data:
            set_redis_data_with_timeout(key, data, ttl)
            logging.debug("Store {} for {} which will expire after {} seconds".format(data, key, ttl))
    else:
        expire_in_seconds = redis.ttl(key)
        logging.debug("Use stored data for {} will expire after {} seconds".format(data, expire_in_seconds))

    return data


def set_dict_if_key_expire(key, ttl, set_func):
    dict_data = get_redis_dict(key)

    if dict_data is None:
        dict_data = set_func()
        # only set data which is not None
        if dict_data:
            set_redis_dict_with_timeout(key, dict_data, ttl)
            logging.debug("Store {} for {} which will expire after {} seconds".format(dict_data, key, ttl))
    else:
        expire_in_seconds = redis.ttl(key)
        logging.debug("Use stored dict for {} will expire after {} seconds".format(dict_data, expire_in_seconds))

    return dict_data
