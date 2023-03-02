#!/bin/bash

set -e
source .venv/bin/activate
alembic upgrade head

if [ "$ENV" == "development" ] 
then
    uvicorn dripdrop.app:app --reload --reload-dir dripdrop --host 0.0.0.0 --port 5000 --log-config ./config/logging.yml
else
    gunicorn dripdrop.app:app -w 2 -k uvicorn.workers.UvicornWorker -b :5000 -c ./config/gunicorn.py
fi
