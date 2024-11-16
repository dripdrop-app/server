FROM python:3.12-alpine
RUN apk add ffmpeg bash curl --no-cache
RUN pip install -U pip
RUN pip install uv
RUN mkdir -p /src
WORKDIR /src
COPY ./uv.lock ./uv.lock
COPY ./pyproject.toml ./pyproject.toml
RUN uv sync
COPY . .
RUN chmod +x ./scripts/*
