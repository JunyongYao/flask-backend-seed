# -*- coding: utf-8 -*-
import logging
import pickle


from abc import ABCMeta, abstractmethod
from app import redis
from app.cache import set_dict_if_key_expire, set_data_if_key_expire, set_redis_dict_with_timeout, \
    set_redis_data_with_timeout
from task.asyncTask import refresh_cache


class CacheABC(object, metaclass=ABCMeta):
    def __init__(self):
        # In order to avoid miss calling parent class's __init__ and reset the value to be 0, only set the value when it
        #  is not set before.
        try:
            getattr(self, "_threshold_value")
        except AttributeError:
            self._threshold_value = 0

    @property
    @abstractmethod
    def cache_key(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def expire_in_seconds(self):
        raise NotImplementedError()

    @property
    def auto_refresh_threshold(self):
        # In case self._threshold_value value was not set before, use a default one.
        return getattr(self, "_threshold_value", 0)

    @auto_refresh_threshold.setter
    def auto_refresh_threshold(self, value):
        if value >= self.expire_in_seconds:
            raise ValueError("Given threshold {} cannot bigger than expire value {}".format(
                value, self.expire_in_seconds))

        self._threshold_value = value

    @abstractmethod
    def data_retrieve_ops(self):
        raise NotImplementedError()

    @abstractmethod
    def get(self) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def refresh(self):
        raise NotImplementedError()

    def clear(self):
        redis.delete(self.cache_key)

    def apply_async_task_if_possible(self):
        # From Redis 2.8, if the key does not exist, return -2; if it has no ttl, return -1.
        left_seconds = redis.ttl(self.cache_key)
        if 0 < left_seconds < self.auto_refresh_threshold:
            logging.info("Apply async task for refresh {}".format(self.cache_key))
            refresh_cache.apply_async(args=[pickle.dumps(self)], serializer='pickle')


class DictCacheABC(CacheABC):
    def get(self) -> dict:
        self.apply_async_task_if_possible()
        return set_dict_if_key_expire(self.cache_key, self.expire_in_seconds, self.data_retrieve_ops)

    def refresh(self):
        dict_data = self.data_retrieve_ops()
        # only set data which is not None
        if dict_data:
            set_redis_dict_with_timeout(self.cache_key, dict_data, self.expire_in_seconds)
        else:
            logging.error("Cannot set dict data for {}".format(self.cache_key))


class DataCacheABC(CacheABC):
    def get(self):
        self.apply_async_task_if_possible()
        return set_data_if_key_expire(self.cache_key, self.expire_in_seconds, self.data_retrieve_ops)

    def refresh(self):
        dict_data = self.data_retrieve_ops()
        # only set data which is not None
        if dict_data:
            set_redis_data_with_timeout(self.cache_key, dict_data, self.expire_in_seconds)
        else:
            logging.error("Cannot set dict data for {}".format(self.cache_key))
