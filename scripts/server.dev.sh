#!/bin/bash

set -e
alembic upgrade head
uvicorn server.main:app --reload --reload-dir server --host 0.0.0.0 --port $SERVER_PORT --log-config ./config/logging.yml