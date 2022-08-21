#!/bin/bash

alembic upgrade head

if [[ $ENV == 'production' ]]; then
    NODE_ENV=$ENV npm --prefix app run build && mv app/build .
    gunicorn server.app:app -w 2 -k uvicorn.workers.UvicornWorker -b :$SERVER_PORT -c config.py
    exit
fi

npm --prefix app start &
SERVER_PID=$!
uvicorn server.app:app --reload --reload-dir server --port $SERVER_PORT &
CLIENT_PID=$!

wait -n $SERVER_PID $CLIENT_PID 