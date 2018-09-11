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

WORKDIR /deploy/app

EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn.conf", "manager:flask_app"]
