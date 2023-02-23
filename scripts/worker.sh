#!/bin/bash

set -e
source .venv/bin/activate

if [ $ENV == "development" ] 
then
    watchfiles 'python worker.py' ./worker.py
else
    supervisord -c ./config/worker.supervisord.conf
fi
