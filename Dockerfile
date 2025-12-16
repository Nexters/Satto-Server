FROM python:3.10

RUN apt-get update && apt-get install -y vim && apt-get install -y less

RUN pip install uv

WORKDIR /satto

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev

COPY ./src /satto/src
