FROM python:3.10

RUN apt-get update && apt-get install -y vim && apt-get install -y less

RUN pip install poetry

# 가상환경 생성하지 않음
RUN poetry config virtualenvs.create false

WORKDIR /satto

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY ./src /satto/src
