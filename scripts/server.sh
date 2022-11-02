#!/bin/bash

set -e
alembic upgrade head
gunicorn server:app -w 2 -k uvicorn.workers.UvicornWorker -b :$SERVER_PORT -c ./config/gunicorn.py