#!/bin/bash

while [ -f $HOME/build.txt ]
do
    echo 'Waiting on build'
    sleep 10
done
touch $HOME/build.txt
[ ! -d $HOME/dripdrop ] || git clone https://github.com/dripdrop-app/server.git
cd $HOME/dripdrop
git pull --rebase
mkdir -p build
\cp -r $HOME/build $HOME/dripdrop
\cp $HOME/.env .
docker compose -f docker-compose.yml build --progress plain
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d
rm $HOME/build.txt