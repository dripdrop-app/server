#!/bin/bash

trap "kill 0" EXIT

source venv/bin/activate
uvicorn server.app:app --reload --reload-dir server --port 5000 & 
# Use below command to test with multiple workers
# gunicorn server.app:app -w 2 -k uvicorn.workers.UvicornWorker -b :5000 -c config.py &  
rq worker --with-scheduler &

wait