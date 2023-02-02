FROM python:3.10
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg
RUN pip install -U pip
RUN pip install poetry
RUN mkdir -p /src
WORKDIR /src
COPY ./poetry.lock ./
COPY ./pyproject.toml ./
RUN poetry install
COPY . .
