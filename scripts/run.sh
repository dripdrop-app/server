ACTION=$1
ENV=$ENV
PROJECT="dripdrop"
COMPOSE_FILE="docker-compose.yml"

build () {
  echo "Building $ENV environment..."
  docker compose -p $PROJECT -f $COMPOSE_FILE build
}

remove() {
  echo "Removing $ENV environment..."
  docker compose -p $PROJECT -f $COMPOSE_FILE down
}

deploy() {
  echo "Deploying to $ENV environment..."
  if [[ $ENV == "development" ]]; then
    remove
  fi
  build
  docker compose -p $PROJECT -f $COMPOSE_FILE up --remove-orphans --wait
}

test () {
  echo "Testing $ENV environment..."
  build
  docker compose -p $PROJECT -f $COMPOSE_FILE run --rm dripdrop-server poetry run python -m unittest discover
}

if [[ $ACTION != "deploy" ]] && [[ $ACTION != "test" ]] && [[ $ACTION != "remove" ]];
then
  echo "Invalid action. Please use 'deploy', 'test' or 'remove'."
  exit 1
fi

if [[ $ENV != "development" ]] && [[ $ENV != "production" ]] && [[ $ENV != "test" ]];
then
  echo "Invalid environment. Please use 'development' or 'production'."
  exit 1
fi

if [[ $ACTION == "deploy" ]]; then
  deploy
elif [[ $ACTION == "test" ]]; then
  test
elif [[ $ACTION == "remove" ]]; then
  remove
fi
