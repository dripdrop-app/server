#!/bin/bash

set -e
source .venv/bin/activate

if [ "$ENV" == "development" ] 
then
    sleep 30s
    watchfiles 'python worker.py' ./worker.py
else
    python worker.py
fi
