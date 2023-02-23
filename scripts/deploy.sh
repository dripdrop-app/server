#!/bin/bash

set -e
docker compose -f docker-compose.prod.yml build --progress plain
docker compose -f docker-compose.prod.yml up --remove-orphans --wait --scale worker=2
