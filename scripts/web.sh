#!/bin/bash

alembic upgrade head
gunicorn server.app:app -w 2 -k uvicorn.workers.UvicornWorker -b :$SERVER_PORT -c config.py