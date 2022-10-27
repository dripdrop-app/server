#!/bin/bash

set -e
alembic upgrade head
gunicorn server.main:app -w 2 -k uvicorn.workers.UvicornWorker -b :$SERVER_PORT -c ./config/gunicorn.py