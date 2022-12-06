FROM python:3.10
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg
RUN pip install -U pip
RUN pip install poetry
RUN mkdir -p /src
WORKDIR /src
COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml
RUN poetry export -f requirements.txt --output requirements.txt
RUN bash -c "python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
COPY . .
