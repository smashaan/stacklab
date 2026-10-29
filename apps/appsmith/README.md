# Appsmith

Build internal tools, dashboards and administrative applications that connect to databases and APIs. This deployment runs Appsmith Commercial Edition and its bundled supporting services in one container.

## Supported setup

- Official Commercial Edition image pinned to `v2.5.1`. Community Edition, `latest`, Kubernetes and external databases are outside this repository's supported configuration.
- One Docker-managed named volume for `/appsmith-stacks`, with an optional absolute host path configured through `.env`.
- HTTP and HTTPS ports bound to the Docker host's loopback address by default.
- Built-in MongoDB, Redis and PostgreSQL services managed inside the Appsmith container.
- Image-native health check supplied by Appsmith.

Appsmith publishes frequent releases, but upstream recommends pinning a version so upgrades remain deliberate. Read the [v2.5.1 release notes](https://github.com/appsmithorg/appsmith/releases/tag/v2.5.1) before deploying and the current release notes before changing the image tag.

## Before you start

- Install Docker Engine and the Docker Compose plugin (`docker compose`).
- Provide at least 2 vCPU, 8 GB RAM and 10 to 15 GB free disk space. Actual production capacity depends on applications, users and connected services.
- Allow outbound HTTPS access to `cs.appsmith.com` for licensing, templates and release information.
- Existing users: the previous Stacklab configuration mounted `/opt/docker/appsmith/data`. Changing to this configuration does not copy that data into the named volume. Preserve the old directory and migrate or restore it before removing the old deployment.
- ARM, Portainer and Dockge have not been tested here.

## Quick start

`.env` is optional because the defaults provide a local, Docker-managed deployment.

From the repository root:

```bash
cd apps/appsmith
docker compose up -d
docker compose ps
```

Initial startup can take several minutes. Wait until the container reports healthy, then open <http://localhost:8080> on the Docker host and create the first administrator account. Create a disposable application, add a widget, deploy it and open its published view as the functional check.

For a remote Docker host, forward the loopback-bound HTTP port through SSH:

```bash
ssh -N -L 8080:127.0.0.1:8080 user@server
```

Then open <http://localhost:8080> on your computer. The default ports are available only through the server's loopback interface.

## Configuration

Copy the example only when changing the defaults:

```bash
cp .env.example .env
# Edit .env, then apply the changes.
docker compose up -d
```

| Variable | Default | Purpose |
|---|---|---|
| `APPSMITH_BIND_ADDRESS` | `127.0.0.1` | Host interface that accepts browser connections |
| `APPSMITH_HTTP_PORT` | `8080` | HTTP port on the Docker host |
| `APPSMITH_HTTPS_PORT` | `8443` | HTTPS port on the Docker host |
| `APPSMITH_STACKS_SOURCE` | `appsmith-stacks` | Named volume or absolute host path mounted at `/appsmith-stacks` |

The mapped HTTPS port is available for Appsmith's own certificate configuration. For broader network access, configure a domain and trusted TLS according to the [upstream custom-domain guidance](https://docs.appsmith.com/getting-started/setup/instance-configuration/custom-domain). Do not expose an instance carrying datasource credentials over untrusted HTTP. Review signup, email verification and authentication settings before inviting users.

Appsmith also writes native settings to `/appsmith-stacks/configuration/docker.env`. Use Admin Settings or the [upstream environment-variable guidance](https://docs.appsmith.com/getting-started/setup/instance-configuration/configure-using-environment-variables) for application configuration. Do not duplicate those native settings in this repository's `.env`, which controls only the maintained Compose deployment.

## Your data

| Source variable | Default volume | Container path | What to preserve |
|---|---|---|---|
| `APPSMITH_STACKS_SOURCE` | `appsmith-stacks` | `/appsmith-stacks` | MongoDB data, configuration, encryption keys, Git data, certificates, logs and backups |

This mount is critical. Losing it can make applications, users and stored datasource credentials unrecoverable. Docker prefixes the named volume with the Compose project name, so keep that project name stable.

To use a host directory, set `APPSMITH_STACKS_SOURCE` to an absolute path outside this checkout. Run `docker compose config` and inspect the resolved mount before applying the change.

> [!WARNING]
> Changing the source does not move existing data. Appsmith sees a new, empty instance until the previous data is migrated or restored. Host directories can also change ownership, permissions and backup requirements.

`docker compose down` retains the named volume. **`docker compose down -v` deletes it.** The volume is not encrypted from the Docker host administrator and is not a backup.

## Back up and restore

Follow the [Appsmith backup and restore guide](docs/backup-and-restore.md). It uses Appsmith's supported `appsmithctl` archive and restores into a separate Compose project.

## Update

Back up and verify the backup first. Read every intervening release note and check [Appsmith upgrade checkpoints](https://docs.appsmith.com/getting-started/setup/instance-management/upgrade-checkpoints). A checkpoint release must start and complete its required work before upgrading past it.

Change the pinned image tag in `compose.yaml`, then run:

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Wait for a healthy state. Sign in as an administrator, review Admin central for pending checkpoints, and test an application in both edit and published views. Do not assume that restoring an old volume into a different Appsmith version is a safe rollback.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| Startup takes several minutes | The container initializes several bundled services. Check `docker compose ps` and `docker compose logs --tail=200 appsmith`. |
| Container restarts or host becomes unresponsive | Confirm that the host meets the memory, CPU and free-space requirements. Inspect the Appsmith logs and Docker events. |
| Browser cannot connect from another computer | The default bind address is loopback. Use the SSH tunnel or configure a trusted LAN address and TLS. |
| Health check remains unhealthy | Query `curl -fsS http://localhost:8080/api/v1/health` on the Docker host and inspect backend logs. The container uses Appsmith's image-native health check. |
| A new instance appears after a Compose change | The project name or `APPSMITH_STACKS_SOURCE` changed, selecting different storage. Preserve both locations before correcting it. |
| Upgrade reports a missed checkpoint | Follow the version named in the logs and the upstream checkpoint recovery procedure. Do not skip checkpoints without understanding the consequences. |

For generic Docker commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

This setup follows the [official Docker installation](https://docs.appsmith.com/getting-started/setup/installation-guides/docker). It keeps the recommended Commercial Edition, pins the current release, uses a Docker-managed volume instead of a repository-relative bind mount, removes the fixed container name and binds both browser ports to loopback. It is intended for evaluation and small single-host deployments. Upstream recommends Kubernetes when high availability and production scaling are required.

- [Official website](https://www.appsmith.com/)
- [Application documentation](https://docs.appsmith.com/)
- [Source repository](https://github.com/appsmithorg/appsmith)
- [Container images](https://hub.docker.com/u/appsmith)
- [Release notes](https://github.com/appsmithorg/appsmith/releases)
- [License](https://github.com/appsmithorg/appsmith/blob/release/LICENSE)
- [Upstream support](https://docs.appsmith.com/product/support)
- [Issue reporting](https://github.com/appsmithorg/appsmith/issues)
- [Security policy](https://github.com/appsmithorg/appsmith/blob/release/SECURITY.md)
