#!/bin/bash

[ ! -d $HOME/dripdrop ] || git clone https://github.com/MohamedRaffik/dripdrop
cd $HOME/dripdrop
git reset --hard HEAD
git config pull.ff only       
git pull
mkdir -p build
\cp -r $HOME/build $HOME/dripdrop
\cp $HOME/.env .
docker system prune -a -f
docker compose -f docker-compose.yml build --progress plain
docker inspect web worker > /dev/null
if [ $? -eq 0 ]; then
        docker compose stop web worker
        docker compose rm -f web worker
fi
docker compose -f docker-compose.yml up -d