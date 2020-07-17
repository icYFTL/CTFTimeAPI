FROM python:3 as ctftimeapi

EXPOSE 8014
RUN mkdir /opt/app
WORKDIR /opt/app

COPY config.json core.py CTFTimeAPI.py requirements.txt .
RUN pip3 install -r requirements.txt