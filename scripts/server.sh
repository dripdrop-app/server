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
    trap "poetry run python ./dripdrop/services/tasker.py --clear-schedule" SIGTERM
    poetry run python ./dripdrop/services/tasker.py --schedule
fi

wait $SERVER_PID
