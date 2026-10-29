# PostgreSQL

PostgreSQL is an open-source relational database focused on reliability, data integrity and extensibility. This setup runs one password-protected PostgreSQL server for local applications and development.

## Supported setup

- Official PostgreSQL `18.6` image, pinned to the current stable patch release.
- One initialized administrator and application database, both named `stacklab` by default.
- SCRAM-SHA-256 host authentication for newly initialized storage.
- Docker-managed cluster storage by default and PostgreSQL access bound to localhost.
- Optional shared-network extension for separately managed applications such as Adminer.

This is a single-server deployment without replication, automated failover, connection pooling or continuous point-in-time recovery. Those require an operational design beyond this app.

## Before you start

- Docker Engine and the Docker Compose plugin (`docker compose`).
- A strong, unique database password.
- Enough durable storage for the database, indexes, write-ahead log and maintenance operations.
- Existing PostgreSQL 17 users: back up with the old image before applying this deployment. PostgreSQL 18 changed the official image mount from `/var/lib/postgresql/data` to `/var/lib/postgresql`. An existing 17 data directory cannot be started directly as an 18 cluster. Follow the major-upgrade guidance below.

The initial administrator can create databases, roles and extensions. Applications should receive separate, least-privileged roles instead of using this administrator account during normal operation.

## Quick start

`.env` is required because the database password has no safe default:

```bash
cd apps/postgres
cp .env.example .env
# Set POSTGRES_PASSWORD to a unique secret in .env.

docker compose config
docker compose up -d
docker compose ps
```

Wait for the service to report healthy, then confirm the server responds:

```bash
docker compose exec postgres sh -c \
  'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version()"'
```

Local programs connect to `127.0.0.1:5432` using the username, password and database from `.env`. Prefer `127.0.0.1` over `localhost` when a client chooses Unix sockets for `localhost`.

For a persistence check, create a disposable table, insert a row, restart PostgreSQL and query it again. Remove the table after the check:

```bash
docker compose exec postgres sh -c \
  'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "CREATE TABLE stacklab_check (value integer)" \
  -c "INSERT INTO stacklab_check VALUES (1)"'

docker compose restart postgres

docker compose exec postgres sh -c \
  'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "TABLE stacklab_check" \
  -c "DROP TABLE stacklab_check"'
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `POSTGRES_PASSWORD` | Required | Password assigned to the initial administrator during first initialization |
| `POSTGRES_USER` | `stacklab` | Initial administrator name |
| `POSTGRES_DB` | `stacklab` | Initial database name and health-check target |
| `POSTGRES_BIND_ADDRESS` | `127.0.0.1` | Host interface accepting PostgreSQL connections |
| `POSTGRES_PORT` | `5432` | PostgreSQL port on the Docker host |
| `POSTGRES_DATA_SOURCE` | `data` | Named volume or absolute host path for the complete PostgreSQL cluster |
| `STACKLAB_NETWORK` | `stacklab` | Existing network used only by the shared-network extension |

The three `POSTGRES_*` initialization values are consumed only when the data source is empty. Editing them later does not rename a database, change a role or rotate its password. Use SQL such as `ALTER ROLE` for an initialized cluster, then update clients and `.env` consistently.

`.env` contains a database administrator password. Keep it out of Git, restrict access and include it in encrypted recovery material. Environment variables are visible to users with Docker administration rights. Docker administrators can already read the database storage and control the container.

> [!WARNING]
> Changing `POSTGRES_DATA_SOURCE` does not copy databases. An empty source initializes a separate cluster. Back up first and inspect the resolved `/var/lib/postgresql` mount with `docker compose config`.

Host-path storage must already exist on a reliable local filesystem and be writable by the image's `postgres` user. Avoid network filesystems unless their durability and locking behavior are explicitly supported for PostgreSQL.

## Shared-network extension

The base port is loopback-only. To let another Compose project connect directly, create the shared network once and attach only trusted applications:

```bash
docker network create stacklab
docker compose -f compose.yaml \
  -f extensions/compose.shared-network.yaml up -d
```

Use the same file arguments for every lifecycle command. With Adminer's matching extension enabled, select PostgreSQL and use server `postgres`, the values from `.env`, and port `5432`. The shared network is not encrypted and any attached container can attempt database authentication.

To disable the extension, first run `down` with both files, then start the base file normally. See the [extension guide](../../docs/extensions.md).

## Network access

Keep the database on loopback unless remote clients genuinely require direct access. For administrative access to a remote Docker host, prefer an SSH tunnel:

```bash
ssh -N -L 5432:127.0.0.1:5432 user@server
```

Changing `POSTGRES_BIND_ADDRESS` only changes Docker's published interface. PostgreSQL roles, `pg_hba.conf`, host firewall rules and transport encryption still determine whether a remote design is safe. Do not publish an unencrypted database port to the internet.

## Your data

| Source | Container path | Contents | Backup need |
|---|---|---|---|
| `POSTGRES_DATA_SOURCE` | `/var/lib/postgresql` | PostgreSQL 18 cluster, configuration, transaction logs and all databases | Essential |
| `.env` | Compose host only | Initial administrator identity, database name and password | Essential and secret |

The PostgreSQL 18 image stores its active data below the versioned `/var/lib/postgresql/18/docker` directory inside this mount. Mount the documented parent path rather than the older PostgreSQL 17 path. Named storage survives `docker compose down`. **`docker compose down -v` deletes it**.

## Back up and restore

Follow the [backup and restore guide](docs/backup-and-restore.md). The documented logical dump covers the configured database. Back up additional databases and roles explicitly if you create them. One dump is not automatically a whole-server recovery set.

## Update

For a patch update within PostgreSQL 18, make and test a logical backup, read the [release notes](https://www.postgresql.org/docs/release/), change the exact image tag in `compose.yaml`, then:

```bash
docker compose pull postgres
docker compose up -d
docker compose ps
```

Confirm health, the server version and representative application queries. PostgreSQL patch releases do not require `pg_upgrade`, but release notes can contain operational actions.

### Major-version upgrades

Never point a new major image at an old major's data directory. For this small general-purpose deployment, the clearest migration is:

1. Back up every database and required global object using the old major image.
2. Preserve the original storage unchanged.
3. Start the new major with an empty data source.
4. Restore and validate the logical backups.
5. Move clients only after application compatibility and recovery checks pass.

Large or low-downtime systems may need `pg_upgrade`, logical replication or managed migration tooling. Follow the [official upgrading documentation](https://www.postgresql.org/docs/current/upgrading.html) rather than adapting the short procedure here.

## Recovery and troubleshooting

| Symptom | Check / action |
|---|---|
| Compose reports a missing password | Copy `.env.example` to `.env` and set `POSTGRES_PASSWORD`. |
| Service stays unhealthy | Inspect `docker compose logs postgres`. Check storage ownership, free space and whether initialization completed. |
| Password edit has no effect | Initialization variables do not modify an existing cluster. Rotate the role password with SQL. |
| Another container cannot resolve `postgres` | Enable the shared-network extension in both projects and confirm they use the same network name. |
| Host client cannot connect | Confirm the published address and port with `docker compose ps`, then check credentials and local firewall rules. |
| PostgreSQL reports incompatible data files | Stop immediately and use the matching old major to make a logical backup. Do not modify the original storage. |
| Host-path storage is denied | Correct ownership and host security policy for the image user. Do not use world-writable permissions. |

For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The deployment uses the PostgreSQL 18 storage layout and initialization behavior from the official image. The current files pin a patch release, allow configurable storage, document recovery and keep cross-project networking optional.

- [Official website](https://www.postgresql.org/)
- [PostgreSQL 18 documentation](https://www.postgresql.org/docs/18/)
- [Official container image and documentation](https://hub.docker.com/_/postgres)
- [Container image source](https://github.com/docker-library/postgres)
- [PostgreSQL source repository](https://git.postgresql.org/gitweb/?p=postgresql.git)
- [Release notes](https://www.postgresql.org/docs/release/)
- [Backup documentation](https://www.postgresql.org/docs/18/backup.html)
- [License](https://www.postgresql.org/about/licence/)
- [Community support](https://www.postgresql.org/support/)
- [Security information](https://www.postgresql.org/support/security/)
- [Container-image issue reporting](https://github.com/docker-library/postgres/issues)
- [Adminer app](../adminer/README.md)
