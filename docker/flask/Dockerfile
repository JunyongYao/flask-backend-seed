FROM  centos/python-36-centos7
MAINTAINER Junyong Yao <ruskeeyao@gmail.com>

USER root
RUN yum install -y libffi-devel mysql-devel python-devel
RUN yum clean all
USER default
# Update PIP
RUN pip install --upgrade pip

ADD requirements.txt /deploy/app/requirements.txt
# Need to have volumn mount to mount the folder /deploy/app/
# if needed, should add proxy  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
RUN pip install -r /deploy/app/requirements.txt

RUN pip install pytz && \
    pip install sqlalchemy && \
    pip install Flask && \
    pip install Flask-SQLAlchemy && \
    pip install Flask-RESTful && \
    pip install flask-restful-swagger && \
    pip install Flask-Mail && \
    pip install Flask-Migrate && \
    pip install Flask-Script && \
    pip install flask-redis && \
    pip install flask-cors && \
    pip install coverage && \
    pip install gunicorn && \
    pip install gevent && \
    pip install celery[redis] >= 4.0.2 && \
    pip install PyYAML && \
    pip install mysqlclient && \
    pip install pyzmq && \
    pip install locustio >= 0.8a2

EXPOSE 5000

WORKDIR /deploy/app

CMD ["gunicorn", "-c", "gunicorn.conf", "manager:flask_app"]
