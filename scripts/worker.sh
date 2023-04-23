#!/bin/bash

set -e

if [ "$ENV" == "development" ] 
then
    PYTHONPATH=. poetry run watchfiles 'python ./dripdrop/worker.py' ./dripdrop
else
    PYTHONPATH=. poetry run python ./dripdrop/worker.py
fi
