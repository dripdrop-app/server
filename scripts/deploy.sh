#!/bin/bash

[ ! -d $HOME/dripdrop ] || git clone https://github.com/MohamedRaffik/dripdrop
cd $HOME/dripdrop
git pull --rebase
mkdir -p build
\cp -r $HOME/build $HOME/dripdrop
\cp $HOME/.env .
docker system prune -a -f
docker compose -f docker-compose.yml build --progress plain
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d