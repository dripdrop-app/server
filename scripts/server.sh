#!/bin/bash

set -e
alembic upgrade head
gunicorn dripdrop:app -w 2 -k uvicorn.workers.UvicornWorker -b :$SERVER_PORT -c ./config/gunicorn.py