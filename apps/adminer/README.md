# Adminer

Adminer is a browser interface for inspecting and managing databases. This deployment runs the standalone official image independently and can connect to a reachable database server or to another Stacklab app through the optional shared-network extension.

## Supported setup

- Official standalone image on the stable `latest` channel. FastCGI and older-major variants are outside this repository's supported configuration.
- MySQL, PostgreSQL, SQLite, SimpleDB and Elasticsearch drivers included by the official image. Other Adminer drivers require a custom image and are not supported here.
- No persistent Adminer data.
- Browser interface bound to the Docker host's loopback address by default.
- Optional shared-network extension for databases in other Compose projects.

The official `latest` tag currently tracks Adminer 6.2.0 and can resolve to a newer release when pulled. See the [official image documentation](https://hub.docker.com/_/adminer) for other image variants and driver details.

## Before you start

- Install Docker Engine and the Docker Compose plugin (`docker compose`).
- Have the database address, database type, username and password ready.
- Confirm that the database accepts connections from the Adminer container or Docker host.
- Use a dedicated, least-privileged database account for routine access. Adminer can execute SQL and alter data with all permissions granted to that account.

## Quick start

`.env` is optional because the default configuration works without it.

From the repository root:

```bash
cd apps/adminer
docker compose up -d
docker compose ps
```

Open <http://localhost:8080> on the Docker host. The Adminer login page should appear. Enter the database system, server address, username, password and database name supplied by the database administrator.

For a remote Docker host, forward the loopback-bound port through SSH (replace `user@server` with your SSH login):

```bash
ssh -N -L 8080:127.0.0.1:8080 user@server
```

Then open <http://localhost:8080> on your computer. The default port is available only through the server's loopback interface.

Adminer does not create database users or bypass database network rules. A successful login depends on the target database configuration.

## Configuration

Copy the example only when changing the defaults or enabling an extension:

```bash
cp .env.example .env
# Edit .env, then apply the changes.
docker compose up -d
```

| Variable | Default | Purpose |
|---|---|---|
| `ADMINER_BIND_ADDRESS` | `127.0.0.1` | Host interface that accepts browser connections |
| `ADMINER_PORT` | `8080` | Browser port on the Docker host |
| `STACKLAB_NETWORK` | `stacklab` | Existing Docker network used by the shared-network extension |

The loopback default limits browser access to the Docker host. Use the SSH tunnel above or change `ADMINER_BIND_ADDRESS` to a trusted LAN address only when other devices require direct access. Do not publish Adminer directly to the internet. Upstream recommends restricting access by source address or adding authentication at the web-server or proxy layer because Adminer has powerful database access and has had security vulnerabilities in the past. Keep the image current and use HTTPS whenever database credentials cross a network.

## Extensions

| Extension | Purpose | Prerequisite |
|---|---|---|
| `compose.shared-network.yaml` | Connect Adminer to apps in other Compose projects | An existing external Docker network |

To connect Adminer to the PostgreSQL app by service name, create the shared network once:

```bash
docker network create stacklab
```

Start Adminer with its shared-network extension:

```bash
docker compose -f compose.yaml \
  -f extensions/compose.shared-network.yaml up -d
```

Run the same command from `apps/postgres` to attach PostgreSQL. In Adminer, select PostgreSQL and use `postgres` as the server. Each app keeps its own lifecycle and private project network while also joining the optional `stacklab` network.

Use the same two `-f` arguments for `config`, `pull`, `logs` and `down`. To disable the extension, run `down` with both files before starting the base deployment again. See the [extension guide](../../docs/extensions.md) for the complete workflow.

## Your data

Adminer is stateless in this deployment. It stores no application database, configuration or uploaded files in a volume. Login sessions and temporary container data disappear when the container is replaced.

The databases managed through Adminer belong to their database servers. Their data, users, permissions, backups and recovery procedures are outside the Adminer container.

## Back up and restore

There is no Adminer application data to back up or restore. Back up every connected database with tools recommended by that database project. Recreating the Adminer container does not restore or remove database data.

## Update

Back up the databases you intend to manage, then read the [Adminer changelog](https://github.com/vrana/adminer/blob/main/CHANGELOG.md). Pull and recreate the container:

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Open the login page and test a connection, read-only query and logout against a noncritical database after updating. Because `latest` is a moving tag, record the resolved image digest before an update when reproducible rollback matters.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| Login page does not open | Run `docker compose ps` and `docker compose logs --tail=100 adminer`. Confirm that `ADMINER_PORT` is not already used. |
| Database server is unreachable | Check the server address, database port, firewall and Docker network. `localhost` inside Adminer refers to the Adminer container. |
| PostgreSQL app name does not resolve | Enable the shared-network extension in both apps and use `postgres` as the server. |
| Authentication fails | Verify the selected database system and credentials directly against the database. Adminer does not create or manage the target account. |
| Expected database type is missing | The official image bundles only its documented drivers. Drivers such as MS SQL, Oracle, Firebird and MongoDB require additional PHP extensions and are outside this setup. |

For general Docker commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The deployment uses the official standalone Adminer image. Unlike the upstream Compose example, the browser interface binds to loopback and cross-project networking is optional. Adminer is a database client, so it has no persistent volume here. Plugins, custom designs, additional PHP database drivers and the FastCGI image are outside the maintained setup.

- [Official website and application documentation](https://www.adminer.org/)
- [Source repository](https://github.com/vrana/adminer)
- [Official container image and image documentation](https://hub.docker.com/_/adminer)
- [Release history](https://github.com/vrana/adminer/blob/main/CHANGELOG.md)
- [License: Apache License 2.0 or GPL 2.0](https://github.com/vrana/adminer/blob/main/LICENSE)
- [Application support and issue reporting](https://github.com/vrana/adminer/issues)
- [Container-image issue reporting](https://github.com/TimWolla/docker-adminer/issues)
- [Security policy](https://github.com/vrana/adminer/blob/main/docs/SECURITY.md)
