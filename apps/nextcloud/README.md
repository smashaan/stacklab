<img src="../../docs/assets/nextcloud/nextcloud_logo.svg" alt="Nextcloud logo" width="150">

# Nextcloud

Nextcloud provides self-hosted file synchronization, sharing and collaboration. This deployment includes the Apache application image, a dedicated MariaDB database, Redis for caching and transactional file locking, and the upstream cron worker for background jobs.

## Supported setup

- Nextcloud `34.0-apache`, tracking maintenance releases within major version 34 without automatic major upgrades.
- MariaDB 11.4 LTS with the required `READ-COMMITTED` isolation level.
- Ephemeral Redis 8.2 for cache, sessions and file locking. Authoritative state remains in Nextcloud and MariaDB.
- Matching cron container with the same image, configuration and application volume.
- Docker-managed volumes and browser access bound to localhost by default. HTTPS reverse-proxy settings are an optional extension.

The newest Nextcloud major is not selected automatically. Review each major upgrade separately and move through supported majors one at a time. Nextcloud All-in-One is upstream's easier full-featured alternative. This repository maintains the microservice image for users who want to manage each service.

## Before you start

- Docker Engine and the Docker Compose plugin (`docker compose`).
- A 64-bit host. Memory needs depend heavily on users, apps, previews and concurrent PHP processes.
- Four strong secrets: database root, database application user, initial Nextcloud administrator and administrator password.
- Enough storage for user files, application state, database growth and separate backups.
- Existing users: the legacy file combined `/opt/docker/nextcloud/data`, `config` and `appdata` mounts with a Compose database volume. Do not start this new layout over those paths. Preserve all old mounts and the database, then plan and test a complete migration.

The administrator values initialize only a fresh installation. Changing them later in `.env` does not rotate the account password. Use Nextcloud's account administration after installation.

## Quick start

`.env` is required because credentials have no safe defaults:

```bash
cd apps/nextcloud
cp .env.example .env

# Generate separate values and place them in the empty password fields.
openssl rand -hex 32

docker compose config
docker compose up -d
docker compose ps
```

Open <http://localhost:8080> on the Docker host. For a remote host, use an SSH tunnel:

```bash
ssh -N -L 8080:127.0.0.1:8080 user@server
```

Sign in with the administrator credentials from `.env`, upload a disposable file, download it, restart the stack and repeat the download. Then check **Administration settings > Overview** for configuration warnings and set background jobs to **Cron** if it is not already selected.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `NEXTCLOUD_DB_ROOT_PASSWORD` | Required | MariaDB administrative secret used for database initialization and recovery |
| `NEXTCLOUD_DB_PASSWORD` | Required | Password used by Nextcloud's database account |
| `NEXTCLOUD_ADMIN_USER` | Required | Initial administrator name on first installation |
| `NEXTCLOUD_ADMIN_PASSWORD` | Required | Initial administrator password on first installation |
| `NEXTCLOUD_DB_NAME` | `nextcloud` | Application database name |
| `NEXTCLOUD_DB_USER` | `nextcloud` | Application database user |
| `NEXTCLOUD_TRUSTED_DOMAINS` | `localhost 127.0.0.1` | Space-separated hostnames or IP addresses accepted by Nextcloud |
| `NEXTCLOUD_BIND_ADDRESS` | `127.0.0.1` | Host interface accepting HTTP connections |
| `NEXTCLOUD_PORT` | `8080` | HTTP port on the Docker host |
| `NEXTCLOUD_PHP_MEMORY_LIMIT` | `512M` | Maximum memory for one PHP request |
| `NEXTCLOUD_UPLOAD_LIMIT` | `1G` | PHP upload and request-data limit |
| `NEXTCLOUD_APACHE_BODY_LIMIT` | `1073741824` | Apache request-body limit in bytes (1 GiB) |
| `NEXTCLOUD_DB_SOURCE` | `database` | Named volume or absolute host path for MariaDB |
| `NEXTCLOUD_DATA_SOURCE` | `nextcloud` | Named volume or absolute host path for the complete Nextcloud tree |

If the host must accept direct LAN access, add its exact LAN address or hostname to `NEXTCLOUD_TRUSTED_DOMAINS`, set the bind address to that LAN IP and secure the host firewall. Plain HTTP is suitable only on a trusted network. Use HTTPS for access beyond the host.

> [!WARNING]
> Changing a storage source does not move data. The database and Nextcloud tree are one consistency set. An empty source can trigger a new installation. Back up both and inspect the resolved mounts before recreating services.

## Reverse-proxy extension

The extension attaches only the web application to an existing shared network and configures trusted forwarding and canonical HTTPS URLs. The database and Redis remain private.

Set `NEXTCLOUD_PUBLIC_HOST`, `NEXTCLOUD_PUBLIC_URL` and `NEXTCLOUD_TRUSTED_PROXIES` in `.env`. The proxy value must identify only the actual proxy container address or a narrow Docker subnet. Do not trust all private networks without reviewing the effect.

```bash
docker network create stacklab-shared
docker compose \
  -f compose.yaml \
  -f extensions/compose.reverse-proxy.yaml \
  up -d
```

Use the same files for every lifecycle command. Keep the host port bound to loopback and configure TLS at the proxy. Removing proxy environment variables later does not automatically remove values already written into Nextcloud configuration. Inspect `config.php` when changing topology. See [shared reverse-proxy guidance](../../docs/reverse-proxy.md) and [upstream proxy configuration](https://docs.nextcloud.com/server/stable/admin_manual/configuration_server/reverse_proxy_configuration.html).

## Your data

| Source | Container path | Contents | Backup need |
|---|---|---|---|
| `NEXTCLOUD_DB_SOURCE` | `/var/lib/mysql` | Users, shares, metadata, app state and file cache | Essential |
| `NEXTCLOUD_DATA_SOURCE` | `/var/www/html` | Configuration, installed apps, themes and user files | Essential |
| `.env` | Compose host only | Database and initial account secrets plus host settings | Essential and secret |

Redis is non-persistent because it stores cache, sessions and locks rather than authoritative data. Named volumes survive `docker compose down`. **`docker compose down -v` deletes both authoritative volumes**.

## Back up and restore

Follow the [backup and restore guide](docs/backup-and-restore.md). A usable backup requires maintenance mode, a database dump and the entire Nextcloud application volume from the same point in time.

## Update

Back up first. Read the [Nextcloud changelog](https://nextcloud.com/changelog/) and image release notes. For maintenance releases within version 34:

```bash
docker compose pull
docker compose up -d
docker compose ps
docker compose exec --user www-data app php occ status
```

Inspect logs and the administration overview, then test login, upload/download, sharing and cron. Never skip a major version. To move beyond 34, update one supported major at a time, satisfy its system requirements and follow its release notes. Restore the matching pre-upgrade database and application backup for rollback. Changing only the image tag cannot undo migrations.

## Troubleshooting

| Symptom | Check / action |
|---|---|
| App waits or restarts | Inspect all service logs. Verify required secrets and database and Redis health with `docker compose ps`. |
| Untrusted-domain page | Add the exact browser hostname or IP to `NEXTCLOUD_TRUSTED_DOMAINS` and recreate the app. |
| Redirect loop or HTTP links behind HTTPS | Verify trusted proxy address, forwarded headers, public URL and protocol extension settings. |
| Upload fails near 1 GiB | Align the PHP, Apache and reverse-proxy limits. The smallest limit wins. |
| Background-job warning | Confirm the `cron` service is running and background jobs are set to Cron in administration settings. |
| Data appears missing | Stop immediately and inspect both resolved storage sources and the Compose project name. Do not initialize over old data. |

For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The service layout comes from the official Apache, MariaDB, Redis and cron example. The images use compatible maintenance channels, startup waits for database health and HTTP binds to loopback. Overlapping mounts, fixed container names, an ineffective Apache port `443` publication and unused volumes from the earlier files have been removed.

- [Official website](https://nextcloud.com/)
- [Container image documentation](https://github.com/nextcloud/docker)
- [Image tags and pinning guidance](https://github.com/nextcloud/docker/wiki)
- [Administration manual](https://docs.nextcloud.com/server/stable/admin_manual/)
- [System requirements](https://docs.nextcloud.com/server/stable/admin_manual/installation/system_requirements.html)
- [Release changelog](https://nextcloud.com/changelog/)
- [Container image](https://hub.docker.com/_/nextcloud)
- [License](https://github.com/nextcloud/server/blob/master/COPYING)
- [Security policy](https://github.com/nextcloud/server/security/policy)
