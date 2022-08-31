FROM python:3.10.3-slim

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    libxml2 \
    gcc \
    vim \
    iputils-ping \
    telnet \
    procps \
    git \
    openjdk-11-jdk && apt-get clean && rm -rf /tmp/* /var/tmp/*


RUN pip install ray
