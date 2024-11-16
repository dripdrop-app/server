FROM python:3.10
RUN apt-get update && apt-get upgrade -y && apt install ffmpeg -y
RUN pip install -U pip
RUN pip install uv
RUN mkdir -p /src
WORKDIR /src
COPY ./uv.lock ./uv.lock
COPY ./pyproject.toml ./pyproject.toml
RUN uv venv
RUN uv sync
VOLUME [ "/src/.venv" ]
COPY . .
RUN chmod +x ./scripts/*
