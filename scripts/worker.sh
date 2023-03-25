#!/bin/bash

set -e

if [ "$ENV" == "development" ] 
then
    poetry run watchfiles 'python worker.py' ./worker.py
else
    poetry run python worker.py
fi
