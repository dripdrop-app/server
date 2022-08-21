#!/bin/bash

set -e

alembic upgrade head
npm --prefix app install 

if [[ $ENV == 'production' ]]; then
    NODE_ENV=$ENV npm --prefix app run build -- --max_old_space_size=512 && mv app/build .
    gunicorn server.app:app -w 2 -k uvicorn.workers.UvicornWorker -b :$SERVER_PORT -c config.py
    exit
fi

set +e

uvicorn server.app:app --reload --reload-dir server --host 0.0.0.0 --port $SERVER_PORT &
SERVER_PID=$!
npm --prefix app start &
CLIENT_PID=$!

while true;
do
    ps -p $SERVER_PID > /dev/null && ps -p $CLIENT_PID > /dev/null
    if [[ $? -eq 1 ]]; then
        exit
    fi
    sleep 5
done