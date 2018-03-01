FROM python:latest
RUN apt-get update
RUN apt-get -y dist-upgrade
ADD . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT python3 messageapi