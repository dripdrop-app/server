#!/bin/sh

set -e

if [[ "$ENV" == "development" ]]; then
    poetry run uvicorn dripdrop.app:app --reload --reload-dir dripdrop --host 0.0.0.0 --port 5000 --log-config ./config/logging.yml &
else
    poetry run uvicorn dripdrop.app:app --host 0.0.0.0 --port 5000 --workers 2 --log-config ./config/logging.yml &
fi

SERVER_PID=$!

if [[ "$ENV" == "production" ]]; then
    poetry run python -m dripdrop.scheduler &
fi

wait $SERVER_PID
