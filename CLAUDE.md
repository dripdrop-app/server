# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

DripDrop downloads and organizes music from YouTube and manages YouTube subscriptions. It is a monorepo with two independently deployed pieces:

- **Server** (`app/`, root `Dockerfile`) — a FastAPI app plus a Celery worker/beat, both defined in the same codebase and image. Backed by Postgres, Redis, and S3-compatible object storage.
- **Client** (`client/`) — a React + Vite + TypeScript SPA (Mantine UI, Redux Toolkit Query), built into its own Docker image.

## Commands

Requires `uv`, `make`, `docker`, `infisical`, and `nvm` (see README.md).

```bash
make install          # install server (uv sync + pre-commit) and client (npm install) deps
make server-dev        # start postgres/redis (docker compose, dev profile) + `fastapi dev app`
make worker-dev         # start postgres/redis + celery worker with autoreload
make client-dev          # start the vite dev server (client/)
make dev                  # run all three of the above together
```

Linting:

```bash
make lint              # uv run ruff check --select I --fix (import sorting only; formatting is via pre-commit's ruff-format hook)
```

Server tests (requires postgres/redis running, e.g. via `make server-dev` or `docker compose --profile dev up -d`):

```bash
make test                                             # ENV=testing pytest tests --cov=app
make test-fast                                        # skip tests marked `long`
ENV=testing uv run pytest tests/routes/music/test_x.py::test_name   # single test
```

Tests requiring real secrets (S3, SMTP, WebDAV, Google API, etc.) can be run via Infisical:

```bash
CMD=test make infisical    # infisical run --env=dev -- make test
```

Database migrations (Alembic, config at `app/db/alembic.ini`):

```bash
make create-migration   # autogenerate a revision from model changes
make migrate             # upgrade to head
```

Client codegen — after changing/adding a FastAPI route, regenerate the RTK Query client against a running server (`http://localhost:8000/api/openapi.json`):

```bash
cd client && npm run generate   # see client/openapi-config.js
```

## Architecture

### Server (`app/`)

- `app/__init__.py` builds the FastAPI `app`, mounting one router per domain under `/api`: `authentication`, `music`, `youtube`, `admin`, `webdav`, `cookies` (`app/routes/<domain>`).
- `app/dependencies.py` defines the auth dependency chain: a user can authenticate via a `Bearer` header (`HeaderUser`) or a session cookie resolved through `app/services/cookie_session.py` (`CookieUser`); `get_authenticated_user` combines both into `AuthUser`, and `AdminUser` further requires `user.admin`. Route handlers depend on `AuthUser`/`AdminUser`/`DatabaseSession`/`RedisClient` rather than reaching for globals.
- `app/db/` holds the SQLAlchemy async engine/session (`session_maker`) and models (`app/db/models/`: `user.py`, `music.py`, `youtube.py`, plus `encrypted.py` for encrypted columns). All models import through `app/db/__init__.py`, which also defines the shared `Base` (with `created_at`/`modified_at`) — import models from `app.db`, not from the submodules directly.
- `app/services/` wraps external integrations used by both routes and tasks: `ytdlp.py`/`invidious.py`/`google.py` (YouTube), `s3.py` (object storage), `ffmpeg.py`/`audiotags.py` (audio processing), `smtp.py` (email), `jwt.py`/`cookie_session.py` (auth), `pubsub.py` (Redis pub/sub for progress updates), `httpclient.py` (shared HTTP client).
- `app/tasks/` is the Celery app (`app.py`). `QueueTask` lets task bodies be plain `async def` functions — it runs them on an event loop instead of requiring sync code — and provides `db_session()`/`redis_client()` context managers for tasks to use their own short-lived connections. Periodic jobs (channel/subscription/category refresh) are only scheduled when `settings.env == ENV.PRODUCTION`.
- `app/settings.py` defines the `ENV` enum (`development`/`production`/`testing`) and a single `Settings` (pydantic-settings, loaded from `.env`). Note the env-dependent overrides applied right after instantiation: in `testing`/`development` the S3 bucket is swapped for `test_aws_s3_bucket`, and in `testing` the database URL is swapped for `test_async_database_url`. New settings that need a test-specific value should follow this same override pattern rather than branching in call sites.
- The Docker image (`Dockerfile`) is a single image for both roles; `ENTRYPOINT ["make"]` with `CMD ["server"]` runs migrations then `uvicorn` (`make server`), while `docker-compose.yml`'s worker equivalent runs `make worker` (celery beat + worker). CI runs the test suite via the same image (`docker compose --profile prod run --rm server test`).

### Client (`client/`)

- Routes/pages live under `client/src/pages`; shared UI under `client/src/components`.
- `client/src/api/` holds the API layer: `client/src/api/generated/` is entirely generated by `npm run generate` from the live OpenAPI schema (via `@rtk-query/codegen-openapi`, config in `client/openapi-config.js`) and split per domain (`musicApi`, `authApi`, `youtubeApi`, `adminApi`, `webdavApi`, `cookiesApi`) — do not hand-edit files in `generated/`; re-run codegen instead. The hand-written files beside it (`auth.ts`, `music.ts`, `youtube.ts`, `cookies.ts`, `webdav.ts`, `tags.ts`) layer app-specific hooks/logic on top of the generated endpoints.
- `client/src/store.ts` wires the single RTK Query `api` reducer/middleware into the Redux store.
- The dev server proxies `/api` to `http://localhost:8000` (`vite.config.ts`); the app is also configured as an installable PWA (`vite-plugin-pwa`) with `/api` explicitly excluded from the service worker's navigation fallback and cache.

### CI/CD (`.github/workflows/ci.yml`)

- `server-lint`/`server-test`/`client-build` gate everything else.
- On `main`, `deploy-server`/`deploy-client` always build and push their image after `bump-version` — there's no path filter gating them, since a push to `main` (including the version-bump commit itself) doesn't reliably signal which side actually changed.
- Versioning is a single repo-wide semver, bumped automatically by `commitizen` from conventional commit messages (config in `pyproject.toml`: `tag_format = "$version"`, `version_provider = "uv"`, `major_version_zero = true`). The `bump-version` job commits the version bump + changelog and pushes the tag back to `main`, and publishes a GitHub Release from the changelog increment. Both images are tagged `latest` and with this shared version.
- `.github/workflows/commit-lint.yml` runs `cz check --rev-range <base>..<head>` on every pull request, rejecting any commit in the PR (other than merge/revert commits, which `cz check` skips automatically) that isn't a valid Conventional Commit.

## Commit message convention

Commits are merged into `main` as-is (no squashing), and their messages directly drive the semver bump above, so every commit must be a [Conventional Commit](https://www.conventionalcommits.org/): `<type>(<optional scope>): <description>`, e.g. `fix(youtube): retry failed subscription refresh`. This is enforced locally by the `commitizen` pre-commit hook (`commit-msg` stage, installed via `make install`) and in CI by `commit-lint.yml` above.

- `feat` → minor bump, `fix`/`perf` → patch bump, `feat!`/`fix!`/a `BREAKING CHANGE:` footer → major bump (once out of `0.x`, per `major_version_zero` in `pyproject.toml`).
- `build`, `chore`, `ci`, `docs`, `refactor`, `style`, `test` do not trigger a version bump on their own.
