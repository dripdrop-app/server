#!/bin/sh

set -e

if [ "$ENV" == "development" ] 
then
    poetry run watchfiles 'python -m dripdrop.worker' ./dripdrop
else
    poetry run python -m dripdrop.worker
fi
