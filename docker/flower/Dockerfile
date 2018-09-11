FROM  centos/python-36-centos7
MAINTAINER Junyong Yao <ruskeeyao@gmail.com>

# Install Flower
ENV FLOWER_VERSION='0.9.1'
RUN pip install flower==$FLOWER_VERSION

# Expose port 5555 so that we can connect to it
EXPOSE 5555

# Run Flower
CMD ["flower", "--port=5555"]
