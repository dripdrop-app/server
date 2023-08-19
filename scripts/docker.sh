#!/bin/bash

set -e

check_option () {
    local option_name=$1
    local option=$2
    shift 2
    local allowed_options=("$@")
    for allowed_option in ${allowed_options[@]}; do
        if [[ $option == $allowed_option ]]; then
            return 0
        fi
    done
    echo "$option_name must be of ( ${allowed_options[@]} )"
    exit 1
}

remove_services () {
    env $DOCKER_ENV docker compose -p $PROJECT -f $COMPOSE_FILE down
}

build_services () {
    docker image build -f ./Dockerfile -t dripdrop/image .
    ENV=$ENVIRONMENT docker compose -p $PROJECT -f $COMPOSE_FILE build
}

[[ ! -f .env ]] && echo ".env not found" && exit 1

ENVIRONMENT="development"
COMPOSE_FILE="docker-compose.dev.yml"
PROJECT="dripdrop"
ENVIRONMENT_VARIABLES=$(cat .env | xargs)

while getopts "a:e:h" option; do
    case $option in
        e)
            check_option "-e" "$OPTARG" "development" "production"
            ENVIRONMENT=$OPTARG
            ;;
        a)
            check_option "-a" "$OPTARG" "remove" "deploy" "test"
            ACTION=$OPTARG
            ;;
        ? | h)
            echo "script usage: $(basename \$0) [-e] environment [-a] action (required)" >&2
            exit 1
            ;;
    esac
done 

if [[ $ACTION == "test" ]]; then
    ENVIRONMENT="testing"
fi  

DOCKER_ENV="$ENVIRONMENT_VARIABLES IMAGE=dripdrop/image ENV=$ENVIRONMENT"

if [[ $ENVIRONMENT == "production" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

if [[ $ACTION == "remove" ]]; then
    remove_services
elif [[ $ACTION == "deploy" ]]; then
    if [[ $ENVIRONMENT == "development" ]]; then
        remove_services
    fi
    build_services
    env $DOCKER_ENV docker compose -p $PROJECT -f $COMPOSE_FILE up --remove-orphans --wait
    if [[ $ENVIRONMENT == "production" ]]; then
        docker restart nginx-proxy
    fi
elif [[ $ACTION == "test" ]]; then

    build_services
    env $DOCKER_ENV docker compose -p $PROJECT -f $COMPOSE_FILE run --rm server poetry run python -m unittest discover
fi
