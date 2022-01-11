#!/bin/bash

trap "kill 0" EXIT

source venv/bin/activate
uvicorn server.app:app --reload --reload-dir server --port 5000 &
rq worker &

wait