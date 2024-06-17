export ACTION=$1
export ENV=$2
PROJECT=dripdrop
DOCKER_IMAGE=$PROJECT/image

set -e

help() {
    echo "Usage: $0 ACTION ENV"
    echo "ENV: development, testing, production"
    echo "ACTION: remove, deploy, test"
    exit 1
}

check_env() {
    if [[ $ENV != "development" && $ENV != "testing" && $ENV != "production" ]]; then
        help
        exit 1
    fi
}

check_action() {
    if [[ $ACTION != "remove" &&  $ACTION != "deploy" && $ACTION != "test" ]]; then
        help
        exit 1
    fi
}

check_env
check_action

DOCKER_COMPOSE_FILE="docker-compose.yml"
if [[ $ENV == "production" ]]; then
  DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
fi

source .env

remove_services() {
    echo "Removing services..."
    docker compose -p $PROJECT -f $DOCKER_COMPOSE_FILE down
}

build_image() {
    echo "Building image..."
    docker image build -f Dockerfile -t $DOCKER_IMAGE .
}

deploy_services() {
    if [[ $ENV == "development" ]]; then
        remove_services
    fi
    build_image
    echo "Deploying services..."
    docker compose -p $PROJECT -f $DOCKER_COMPOSE_FILE up --remove-orphans --wait
}

test_services() {
    build_image
    echo "Testing services..."
    docker compose -p $PROJECT -f $DOCKER_COMPOSE_FILE run --rm dripdrop-server poetry run python -m unittest discover
}

if [[ $ACTION == "remove" ]]; then
    remove_services
elif [[ $ACTION == "deploy" ]]; then
    deploy_services
elif [[ $ACTION == "test" ]]; then
    test_services
fi
