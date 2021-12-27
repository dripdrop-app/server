#!/bin/bash

set -e

rq worker &
npm --prefix app start &
uvicorn --reload --reload-dir=server server.app:app --port 5000