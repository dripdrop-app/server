#!/bin/bash

if [ "$ENV" == "development" ]
then
    docker build --tag dripdrop-dev -f ./dockerfiles/Dockerfile.dev .
    docker stack rm dripdrop-dev
    while : ; do
        docker stack ps dripdrop-dev > /dev/null 2>&1
        if [ $? != 0 ]; then
            break
        fi
        sleep 1s
    done 
    export $(cat .env | xargs) && docker stack deploy --compose-file docker-compose.dev.yml --prune dripdrop-dev
else
    docker build --tag dripdrop -f ./dockerfile/Dockerfile .
    export $(cat .env | xargs) && docker stack deploy --compose-file docker-compose.prod.yml --prune dripdrop
fi
