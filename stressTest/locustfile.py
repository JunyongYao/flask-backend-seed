import random
import string

from gevent import monkey
monkey.patch_all()

from collections import namedtuple
from locust import HttpLocust, TaskSet, task, events
from concurrent import futures
import logging

# Need to install locust via source code because pypi's version is not as latest as python 3.X supported. The command is
# pip install git+https://github.com/locustio/locust.git

###############################################################
# How to test
# 1. start api service, EG, the service is at http://127.0.0.1:5000
# 2. run locust --host=http://127.0.0.1:5000   or  locust --host=[Your Web URL]
# 3. open browser to access http://127.0.0.1:8089
#   Go to localhost:8089 in your browser and type in numbers and click start.
#   or POST localhost:8089/swarm with {"locust_count": 3, "hatch_rate": 1}
#   or Run with --no-web configuration and has -c -r specified
# 4. config simulated number and run


Url_info = namedtuple("Url_info", "url, type, head_data, body_data")


class UserBehaviorTasks(TaskSet):
    min_wait = 1000
    max_wait = 9000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None

    @staticmethod
    def generate_random_string(length):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(length))

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        # create a user
        name = self.generate_random_string(10)
        # If url is provided, it will not upload img and use the given one
        with self.client.post("/api/test/get_test_user", {"name": name}, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Cannot create mock user with info {}".format(response.content))
                raise RuntimeError("Cannot get usermock")

            # assume the token will be provided by test mock api
            self.token = response["token"]

    @task(1)
    def user_change_name(self):
        new_name = self.generate_random_string(5)
        # this should follow format ("url, type, head_data, body_data") in a list
        url_info_list = [("/api/sample/user_info", "put", {"Token": self.token}, {"NewName": new_name}), ]
        self.send_concurrent_http_request(url_info_list)

    @task(5)
    def user_get_name(self):
        url_info_list = [("/api/sample/user_info", "get", {'Token': self.token}, None), ]
        self.send_concurrent_http_request(url_info_list)

    def send_concurrent_http_request(self, url_info_list):
        result = True
        with futures.ThreadPoolExecutor(len(url_info_list)) as executor:
            future_to_url = {executor.submit(self.send_http_request, url_info): url_info[0] for url_info in url_info_list}
            for future in futures.as_completed(future_to_url):
                url = future_to_url[future]
                if future.exception() is not None:
                    logging.error("{} generated an exception {}".format(url, future.exception()))
                    result = False
                elif not future.result():
                    logging.error("The request for {} failed".format(url))

        return result

    def send_http_request(self, url_info):
        url_info = Url_info._make(url_info)
        if url_info.type == "get":
            response = self.client.get(url_info.url, data=url_info.body_data, headers=url_info.head_data)
        elif url_info.type == "post":
            response = self.client.post(url_info.url, data=url_info.body_data, headers=url_info.head_data)
        elif url_info.type == "put":
            response = self.client.put(url_info.url, data=url_info.body_data, headers=url_info.head_data)
        elif url_info.type == "delete":
            response = self.client.delete(url_info.url, data=url_info.body_data, headers=url_info.head_data)
        else:
            events.request_failure.fire(request_type=url_info.type, name=url_info.url,
                                        response_time=1, exception=RuntimeError)
            logging.error("Unsupported type {}".format(url_info.type))
            return False

        return response.status_code == 200


class WebsiteUser(HttpLocust):
    task_set = UserBehaviorTasks

