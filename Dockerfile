FROM centos:8 AS developer
RUN yum install python38 -y
RUN yum install git -y
RUN python3 -V
COPY requirements.txt /req/requirements.txt
WORKDIR /req
RUN  pip3 install -r requirements.txt
WORKDIR /app
RUN rm -rf /req
EXPOSE 5000
CMD ["sleep", "infinity"]