PROJECT=dripdrop
COMPOSE_FILE=docker-compose.yml
SERVICES=dripdrop-postgres dripdrop-redis

bws-gen-env:
	bws run --project-id df08fac1-cd3f-48e5-9299-b174001ca3c6 env | sort > .env
lint:
	uv run ruff check
build-dev:
	ENV=development docker compose -p $(PROJECT) -f $(COMPOSE_FILE) build
build-test:
	ENV=testing docker compose -p $(PROJECT) -f $(COMPOSE_FILE) build
remove:
	docker compose -p $(PROJECT) -f $(COMPOSE_FILE) down
test: build-test
	ENV=testing docker compose -p $(PROJECT) -f $(COMPOSE_FILE) run --rm dripdrop-server uv run python -m unittest discover -vv
test-local: bws-gen-env test
deploy-dev: remove bws-gen-env build-dev
	ENV=development docker compose -p $(PROJECT) -f $(COMPOSE_FILE) up --remove-orphans --wait
deploy-local: remove bws-gen-env build-dev
	ENV=development docker compose -p $(PROJECT) -f $(COMPOSE_FILE) up $(SERVICES) --remove-orphans --wait
run-local-server:
	ENV=development ./scripts/server.sh
run-local-worker:
	ENV=development ./scripts/worker.sh
