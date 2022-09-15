#!/bin/bash

alembic upgrade head
npm --prefix app install

poetry run uvicorn server.app:app --reload --reload-dir server --host 0.0.0.0 --port $SERVER_PORT &
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