#!/bin/bash

set -e
source .venv/bin/activate
alembic upgrade head
