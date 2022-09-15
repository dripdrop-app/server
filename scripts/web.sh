#!/bin/bash

poetry run alembic upgrade head
poetry run gunicorn server.app:app -w 2 -k uvicorn.workers.UvicornWorker -b :$SERVER_PORT