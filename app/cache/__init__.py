# -*- coding: utf-8 -*-
import json

from app import redis


def set_redis_dict(key, data):
    data_str = json.dumps(data)
    redis.set(key, data_str)


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


def get_redis_data(key):
    data = redis.get(key)
    if data:
        data = data.decode('utf-8')

    return data
