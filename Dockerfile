FROM python:3.10-alpine
RUN apk update && apk upgrade && apk add ffmpeg && apk add curl
RUN pip install -U pip
RUN pip install poetry
RUN mkdir -p /src
WORKDIR /src
COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml
RUN poetry config virtualenvs.in-project true
RUN poetry install
VOLUME [ "/src/.venv" ]
COPY . .
RUN chmod +x ./scripts/*
