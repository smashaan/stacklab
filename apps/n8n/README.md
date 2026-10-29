# n8n

n8n is a workflow-automation platform for connecting services, transforming data and running scheduled or event-driven processes. This setup maintains one self-hosted n8n instance with its supported SQLite database.

## Supported setup

- Official n8n image pinned to stable version `2.45.5`. Upgrades are manual because application and database migrations may occur.
- Single instance with SQLite and internal task runners. PostgreSQL, queue mode, Redis and external runners are outside this maintained base.
- Explicit credential-encryption key and Docker-managed application/file volumes by default.
- Browser access bound to localhost. Public HTTPS and webhook URL settings are provided as an optional reverse-proxy extension.

SQLite is suitable for development and smaller single-instance deployments. Use n8n's official PostgreSQL guidance when an instance has sustained workloads, multiple users or operational requirements beyond this scope.

## Before you start

- Docker Engine and the Docker Compose plugin (`docker compose`).
- A persistent encryption key. Losing or changing it makes stored credentials unusable.
- Enough memory for n8n and the workflows you run. Code and community nodes can consume additional resources.
- Existing users: the legacy Stacklab setup used `/opt/docker/n8n/data` and did not set an explicit encryption key. Point `N8N_DATA_SOURCE` to that directory before recreating it, and preserve the key stored in its settings file. Do not introduce a different key to an existing database.

n8n workflows can call external services and some nodes can run code, commands or access files. Treat workflow editors and imported workflows as privileged. Review community nodes before installation and use n8n's security audit regularly.

## Quick start

`.env` is required because the encryption key has no safe default:

```bash
cd apps/n8n
cp .env.example .env

# Paste this command's output after N8N_ENCRYPTION_KEY= in .env.
openssl rand -hex 32

docker compose config
docker compose up -d
docker compose ps
```

Open <http://localhost:5678> on the Docker host and create the instance-owner account. For a remote host, keep the loopback binding and use an SSH tunnel:

```bash
ssh -N -L 5678:127.0.0.1:5678 user@server
```

Then open the same localhost URL on your computer. Create a manual-trigger workflow with an **Edit Fields** node, execute it, restart n8n and confirm the workflow and execution remain visible.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `N8N_ENCRYPTION_KEY` | Required | Encrypts credentials stored by n8n and must remain stable and secret |
| `N8N_TIME_ZONE` | `Etc/UTC` | Container and schedule-node time zone using an IANA name |
| `N8N_BIND_ADDRESS` | `127.0.0.1` | Host address accepting browser connections |
| `N8N_PORT` | `5678` | Browser port on the Docker host |
| `N8N_DATA_SOURCE` | `data` | Named volume or absolute host path for SQLite, settings and keys |
| `N8N_FILES_SOURCE` | `files` | Named volume or absolute host path available to file nodes as `/files` |
| `SHARED_NETWORK_NAME` | `stacklab-shared` | Existing network used only by the shared-network extension |

The `.env` file contains a credential-decryption secret. Keep it out of Git, restrict its permissions and include it in encrypted backups. Only `/files` is allowed for file-access nodes by this configuration.

> [!WARNING]
> Changing either storage source does not move data. An empty data source starts a new instance. The old encryption key and database must remain together. Back up first and inspect the resolved mounts with `docker compose config`.

## Extensions

See the [shared extension workflow](../../docs/extensions.md).

| Extension | Purpose | Prerequisite |
|---|---|---|
| `compose.shared-network.yaml` | Connect workflows to other Stacklab apps by service name | Existing external Docker network |
| `compose.reverse-proxy.yaml` | Set the canonical HTTPS editor and webhook URLs | A trusted reverse proxy already providing TLS |

For shared networking:

```bash
docker network create stacklab-shared
docker compose -f compose.yaml -f extensions/compose.shared-network.yaml up -d
```

For a reverse proxy, set `N8N_PUBLIC_HOST` and the trailing-slash `N8N_PUBLIC_URL` in `.env`, then apply both extensions so the proxy can reach n8n through the shared network:

```bash
docker compose \
  -f compose.yaml \
  -f extensions/compose.shared-network.yaml \
  -f extensions/compose.reverse-proxy.yaml \
  up -d
```

The proxy must sanitize forwarded headers, pass the original host/protocol and be the only trusted hop represented by `N8N_PROXY_HOPS=1`. Keep the host port on loopback. See [reverse-proxy guidance](../../docs/reverse-proxy.md) and n8n's [webhook configuration](https://docs.n8n.io/hosting/configuration/configuration-examples/webhook-url/).

## Your data

| Source | Container path | Contents | Backup need |
|---|---|---|---|
| `N8N_DATA_SOURCE` | `/home/node/.n8n` | SQLite database, workflows, credentials, encryption settings and instance state | Essential |
| `N8N_FILES_SOURCE` | `/files` | Files read or written by workflows | Essential when workflows depend on them |
| `.env` | Compose host only | Explicit encryption key and host settings | Essential and secret |

Named volumes survive `docker compose down`. **`docker compose down -v` deletes both**. Credentials inside the database are encrypted, but workflow definitions, execution data and files may still contain sensitive information.

## Back up and restore

Follow the [backup and restore guide](docs/backup-and-restore.md). It stops n8n for a consistent SQLite copy and keeps the database, encryption key and workflow files together.

## Update

Back up and read the [release notes](https://github.com/n8n-io/n8n/releases), including breaking changes. Change the image tag in `compose.yaml` to the intended stable version, then:

```bash
docker compose pull n8n
docker compose up -d
docker compose ps
```

Repeat the representative workflow, credential and webhook checks. Changing the tag back does not necessarily reverse database migrations. Restore the matching pre-update backup when rollback is necessary.

## Troubleshooting

| Symptom | Check / action |
|---|---|
| Compose reports a missing encryption key | Copy `.env.example`, generate a key and set `N8N_ENCRYPTION_KEY`. |
| Stored credentials cannot decrypt | The encryption key changed or the wrong data source is mounted. Restore the original matching key and data together. |
| Browser cannot connect remotely | Loopback is intentional. Use the SSH tunnel or a secured reverse proxy. |
| OAuth redirects or webhook URLs are wrong | Apply the reverse-proxy extension and verify the public host, URL, forwarded headers and proxy-hop count. |
| Workflow file access is denied | Use a path below `/files` and verify ownership of a host-path source. |
| SQLite reports locking or corruption | Stop writes, preserve the volume and restore a known-good backup. Do not run multiple n8n instances against one SQLite file. |

For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The deployment uses n8n's supported single-instance SQLite model. It removes the earlier fixed container name, machine-specific `/opt` path, public port binding and disabled secure-cookie setting. The image is pinned, the encryption key is required and public URL settings stay outside the local base configuration.

- [Official website](https://n8n.io/)
- [Docker installation](https://docs.n8n.io/hosting/installation/docker/)
- [Database guidance](https://docs.n8n.io/hosting/configuration/supported-databases-settings/)
- [Environment-variable reference](https://docs.n8n.io/hosting/configuration/environment-variables/)
- [Security guidance](https://docs.n8n.io/hosting/securing/)
- [Security audit](https://docs.n8n.io/hosting/securing/security-audit/)
- [Source repository](https://github.com/n8n-io/n8n)
- [Container image](https://hub.docker.com/r/n8nio/n8n)
- [Release notes](https://github.com/n8n-io/n8n/releases)
- [License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md)
- [Security policy](https://github.com/n8n-io/n8n/security/policy)
