#!/bin/bash

source venv/bin/activate
dotenv -f .env run uvicorn --reload --reload-dir=server server:app --port 5000
deactivate