FROM python:3.10
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install ffmpeg
RUN pip install -U pip
RUN pip install poetry
RUN mkdir -p /src
WORKDIR /src
COPY . .
RUN poetry config virtualenvs.in-project true
RUN poetry install
VOLUME [ "/src/.venv" ]
RUN chmod +x ./scripts/*
