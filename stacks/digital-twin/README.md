# Digital twin

Digital twin is a small Stacklab application for cataloging rooms, devices, components, purchases and device telemetry. The stack combines PostgreSQL, an authenticated FastAPI service and a lightweight browser interface served through Nginx.

## Supported setup

- PostgreSQL `18.6` with an initialized inventory schema and lookup seed data.
- FastAPI `0.162.0`, SQLAlchemy `2.1.6`, Psycopg `3.3.6` and Pydantic `2.14.1` on Python 3.13.
- Password login with short-lived HS256 access tokens and Argon2 password hashing.
- Browser dashboard for inventory totals, device listing and device creation.
- Authenticated API endpoints for rooms, devices, components, purchases, lookups, relationships and sensor readings.
- Only the Nginx frontend is published, on the Docker host's loopback interface by default. PostgreSQL and FastAPI remain internal.
- Docker-managed database storage by default.

This remains an early single-user administrative application, not a home-automation controller or a general IoT ingestion platform. It has no password-reset workflow, multi-tenant authorization, database migrations, bulk import or high-volume telemetry retention policy.

## Before you start

- Docker Engine and the Docker Compose plugin (`docker compose`).
- OpenSSL for generating the token-signing secret.
- A unique database password and initial administrator password.
- Existing users: the legacy stack was not runnable as committed and used PostgreSQL 16 storage at `/opt/docker/postgres/data`. Do not attach that directory to PostgreSQL 18. Make a PostgreSQL 16 logical dump first and restore it into an empty PostgreSQL 18 source after reviewing schema compatibility.

## Quick start

`.env` is required:

```bash
cd stacks/digital-twin
cp .env.example .env

# Put this output after DIGITAL_TWIN_SECRET_KEY= in .env.
openssl rand -hex 32
```

Set unique values for `DIGITAL_TWIN_DB_PASSWORD` and `DIGITAL_TWIN_ADMIN_PASSWORD`. The administrator password must contain at least 12 characters. Then validate, build and start the stack:

```bash
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

Open <http://localhost:3000> and sign in with `DIGITAL_TWIN_ADMIN_USER` and `DIGITAL_TWIN_ADMIN_PASSWORD`. Verify the seeded rooms and device types load, add a disposable device, restart the stack and confirm the device remains. The OpenAPI interface is available at <http://localhost:3000/docs>. Use **Authorize** with a token obtained from `/api/v1/auth/token`.

For a remote Docker host, keep the loopback binding and use an SSH tunnel:

```bash
ssh -N -L 3000:127.0.0.1:3000 user@server
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DIGITAL_TWIN_DB_PASSWORD` | Required | PostgreSQL application-owner password |
| `DIGITAL_TWIN_SECRET_KEY` | Required | JWT signing secret with at least 32 random characters |
| `DIGITAL_TWIN_ADMIN_PASSWORD` | Required | Initial administrator password with at least 12 characters |
| `DIGITAL_TWIN_DB_USER` | `digital_twin` | Initial PostgreSQL role |
| `DIGITAL_TWIN_DB_NAME` | `digital_twin` | Initial PostgreSQL database |
| `DIGITAL_TWIN_ADMIN_USER` | `admin` | Initial application administrator name |
| `DIGITAL_TWIN_ACCESS_TOKEN_MINUTES` | `30` | Login-token lifetime in minutes |
| `DIGITAL_TWIN_BIND_ADDRESS` | `127.0.0.1` | Host interface accepting browser connections |
| `DIGITAL_TWIN_PORT` | `3000` | Browser port on the Docker host |
| `DIGITAL_TWIN_DB_SOURCE` | `database` | Named volume or absolute host path for the PostgreSQL cluster |

Database initialization values and the administrator credentials are used only when their records do not exist. Editing `.env` later does not rename the database or reset an existing administrator password. A dedicated password-management workflow must be implemented before this application is used by more than one trusted administrator.

Changing the signing secret immediately invalidates all issued tokens. Keep `.env` private and include it in encrypted recovery material.

> [!WARNING]
> Changing `DIGITAL_TWIN_DB_SOURCE` does not copy the database. An empty source initializes a new application. Back up first and inspect the resolved `/var/lib/postgresql` mount with `docker compose config`.

## Architecture

```text
Browser -> Nginx frontend :3000 -> FastAPI backend :8000 -> PostgreSQL :5432
```

Only the frontend has a host port. Nginx serves static assets and proxies same-origin API, health and documentation requests, avoiding public database or backend ports and browser CORS configuration.

The SQL initialization file runs only when PostgreSQL creates empty storage. SQLAlchemy also creates missing tables at backend startup, but it does not perform schema migrations. Any future schema change must add a deliberate migration mechanism before existing deployments are upgraded.

## Authentication and exposure

All inventory and telemetry endpoints require a bearer token. `/health`, `/docs` and `/openapi.json` are reachable without a token, but API operations still reject unauthenticated requests. The browser stores the token in session storage, so closing the browser session removes it.

Loopback HTTP is suitable for local access and SSH tunneling. Before direct LAN or internet exposure, place the frontend behind an HTTPS reverse proxy, add rate limiting, review token and password workflows, and perform an application security review. This custom application has not undergone an independent security audit.

## Your data

| Source | Container path | Contents | Backup need |
|---|---|---|---|
| `DIGITAL_TWIN_DB_SOURCE` | `/var/lib/postgresql` | Accounts, inventory, relationships, purchases and telemetry | Essential |
| `.env` | Compose host only | Database password, signing secret and bootstrap administrator values | Essential and secret |
| Source tree | Images at build time | Backend, frontend and schema definition | Reproducible from Git |

Named storage survives `docker compose down`. **`docker compose down -v` deletes the database**.

## Back up and restore

Follow the [backup and restore guide](docs/backup-and-restore.md). The database dump and matching `.env` form one recovery set.

## Update

Back up and complete a restore test first. Review changes to the Python dependencies, PostgreSQL image, Nginx image, database schema and application source. Rebuild and recreate:

```bash
docker compose build --pull
docker compose pull database
docker compose up -d
docker compose ps
docker compose logs --tail=100 backend frontend database
```

Test login, summary counts, device creation, API documentation and representative telemetry queries. PostgreSQL major upgrades require logical migration or `pg_upgrade`. Never attach an old-major data directory to a new-major image.

## Recovery and troubleshooting

| Symptom | Check / action |
|---|---|
| Compose reports missing values | Fill all required `.env` entries and rerun `docker compose config`. |
| Backend repeatedly restarts | Inspect backend logs. Confirm secrets meet minimum lengths and the database is healthy. |
| Login fails after editing `.env` | Bootstrap credentials do not overwrite an existing user. Restore the previous password or use a controlled database recovery procedure. |
| Browser shows no data | Inspect frontend and backend logs, then request `/health`. Confirm the backend container is healthy. |
| Device creation returns conflict | Verify referenced room, type and manufacturer records and check uniqueness constraints. |
| Existing PostgreSQL directory is incompatible | Stop and use the matching old major to create a logical dump. Preserve the original directory unchanged. |
| Host port `3000` is occupied | Change `DIGITAL_TWIN_PORT` and recreate the frontend. |

For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

This replaces a prototype that could not build. Its frontend image was empty, backend modules and schemas were missing, SQL initialization order was invalid, and Compose used fixed names and machine-specific storage. The repaired stack starts with a smaller inventory workflow that can be expanded later.

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL documentation](https://www.postgresql.org/docs/18/)
- [Nginx documentation](https://nginx.org/en/docs/)
- [FastAPI source and security policy](https://github.com/fastapi/fastapi)
- [PostgreSQL security information](https://www.postgresql.org/support/security/)
- [Nginx security advisories](https://nginx.org/en/security_advisories.html)
