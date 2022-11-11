#!/bin/bash

set -e
alembic upgrade head
uvicorn dripdrop:app --reload --reload-dir dripdrop --host 0.0.0.0 --port $SERVER_PORT --log-config ./config/logging.yml