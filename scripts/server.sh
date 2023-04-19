#!/bin/bash

set -e

if [ "$ENV" == "development" ] 
then
    poetry run uvicorn dripdrop.app:app --reload --reload-dir dripdrop --host 0.0.0.0 --port 5000 --log-config ./config/logging.yml &
else
    poetry run uvicorn dripdrop.app:app --host 0.0.0.0 --port 5000 --workers 4 --log-config ./config/logging.yml &
fi

SERVER_PID=$!

poetry run alembic upgrade head

if [ "$ENV" == "production" ]
then
    trap "PYTHONPATH=. poetry run python ./dripdrop/tasker.py --clear-schedule" SIGTERM
    PYTHONPATH=. poetry run python ./dripdrop/tasker.py --schedule
fi

wait $SERVER_PID
