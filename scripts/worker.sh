#!/bin/bash

set -e

uv run alembic upgrade head

if [[ "$ENV" == "development" ]]; then
    uv run watchfiles 'python -m dripdrop.worker' ./dripdrop
else
    uv run python -m dripdrop.worker
fi
