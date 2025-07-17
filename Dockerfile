FROM python:3.10

RUN apt-get update && apt-get install -y vim && apt-get install -y less

WORKDIR /satto

COPY ./src /satto/src

RUN pip install --no-cache-dir --upgrade -r /requirements.txt
