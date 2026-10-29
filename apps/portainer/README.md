# Portainer

Portainer is a web interface for managing container environments. This setup runs Portainer Community Edition against the local, rootful Docker Engine through its Unix socket.

## Supported setup

- Official Portainer CE `2.45.3` LTS image, pinned to an exact security-patch release.
- One local Docker Standalone environment through `/var/run/docker.sock`.
- Native HTTPS on port `9443` with Portainer's generated self-signed certificate.
- Docker-managed `/data` volume by default and browser access bound to localhost.

Edge Agents, remote Agents, Swarm, Kubernetes, Podman, Business Edition and rootless Docker are outside this base setup. Port `8000` is not published because it is only needed for Edge-agent tunnels.

## Before you start

- A supported, current Docker Engine and Docker Compose plugin (`docker compose`).
- A rootful Linux Docker host with access to `/var/run/docker.sock`.
- A browser that can reach the chosen bind address.
- Existing users: the legacy stack stored data at `/opt/docker/portainer/data`. Set `PORTAINER_DATA_SOURCE` to that exact directory before recreating the container, and back it up first.

> [!CAUTION]
> Access to Portainer is effectively administrative access to the Docker host. The mounted Docker socket can control containers, mount host files and obtain root-level host access. Give Portainer administrator rights only to fully trusted users, keep the UI off the public internet and do not weaken access controls because the service runs in a container.

Upstream's standard Docker instructions assume SELinux is disabled. SELinux and rootless Docker require different, security-sensitive configuration. Follow Portainer's current platform guidance instead of adding broad privileges to this file.

## Quick start

The defaults need no `.env` file:

```bash
cd apps/portainer
docker compose config
docker compose up -d
docker compose ps
docker compose logs portainer
```

Open <https://localhost:9443>. A certificate warning is expected for the generated self-signed certificate. Verify that the address is your host before proceeding.

On a fresh instance, find the one-time `setup_token=` value in the startup logs, enter it when prompted, and complete initialization within five minutes. Create the initial administrator with a unique password of at least 12 characters, skip Edge setup, and select the automatically detected local environment.

Confirm that Portainer lists the expected local containers and can display the logs for one non-sensitive test container. Restart Portainer and verify that the administrator account and local environment remain available:

```bash
docker compose restart portainer
docker compose ps
```

For a remote Docker host, keep the loopback binding and use an SSH tunnel:

```bash
ssh -N -L 9443:127.0.0.1:9443 user@server
```

Then open <https://localhost:9443> locally.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PORTAINER_BIND_ADDRESS` | `127.0.0.1` | Host interface accepting HTTPS connections |
| `PORTAINER_HTTPS_PORT` | `9443` | Portainer HTTPS port on the Docker host |
| `PORTAINER_DATA_SOURCE` | `data` | Named volume or absolute host path for persistent Portainer data |

Copy `.env.example` to `.env` only when an override is needed. Binding to a LAN address expands access to a host-administration interface. Combine it with a firewall, trusted network and planned TLS configuration. Use `0.0.0.0` only when every host interface should accept connections.

> [!WARNING]
> Changing the data source does not move Portainer's database or settings. An empty source starts a fresh instance and exposes the initialization flow. Back up first and inspect the resolved `/data` mount with `docker compose config`.

Portainer does not need Stacklab's shared Docker network. It manages local containers through the Docker socket and can inspect their networks without joining them.

## TLS and reverse proxies

Portainer creates a self-signed certificate for HTTPS by default. For trusted browser TLS, configure a certificate through Portainer or place it behind an authenticated HTTPS reverse proxy according to the [official SSL guidance](https://docs.portainer.io/advanced/ssl).

Keep the host port on loopback when a reverse proxy connects locally. If the proxy is containerized, plan the connectivity carefully. Attaching Portainer to a shared network increases the number of containers that can reach its privileged management API. Follow the [shared reverse-proxy guidance](../../docs/reverse-proxy.md), including WebSocket support and access restrictions.

## Your data

| Source | Container path | Contents | Backup need |
|---|---|---|---|
| `PORTAINER_DATA_SOURCE` | `/data` | Portainer database, users, settings, certificates, environment metadata and Portainer-managed stack definitions | Essential and sensitive |
| Docker socket | `/var/run/docker.sock` | Live control channel to the host Docker Engine, not persistent app data | Never back up or copy |

Portainer's backup covers its own configuration, not managed containers, images, volumes or application data. Back up every managed workload separately. Named storage survives `docker compose down`. **`docker compose down -v` deletes it**.

## Back up and restore

Follow the [backup and restore guide](docs/backup-and-restore.md). Portainer's supported restore workflow requires a fresh instance with an empty `/data` source, so test recovery on a disposable Docker host rather than beside a production daemon.

## Update

Back up Portainer and review the [release notes](https://github.com/portainer/portainer/releases) plus [upgrade guidance](https://docs.portainer.io/start/upgrade/docker). Change the exact image tag in `compose.yaml`, then:

```bash
docker compose pull portainer
docker compose up -d
docker compose ps
docker compose logs --tail=100 portainer
```

Sign in, confirm the reported version and inspect the local environment. If Agents are added later, Portainer requires their versions to match the Server version. Database migrations can make image-only rollback unsafe. Restore the matching pre-update backup into an empty data source when rollback is required.

## Recovery and troubleshooting

| Symptom | Check / action |
|---|---|
| Browser reports an untrusted certificate | This is expected with the generated certificate. Confirm the host and port, or install a trusted certificate. |
| Fresh setup says the instance timed out | Run `docker compose restart portainer`, reload the page and finish setup within five minutes. |
| Setup appears after a working installation | Stop and verify that the intended non-empty source is mounted at `/data`. Do not create a replacement account until the data problem is understood. |
| Portainer cannot reach Docker | Confirm Docker is running and the socket exists. Review socket permissions and logs. Do not expose the unauthenticated Docker TCP API as a shortcut. |
| Port `9443` is already allocated | Set an unused `PORTAINER_HTTPS_PORT` in `.env`, then recreate the container. |
| Remote browser cannot connect | Prefer the documented SSH tunnel. For LAN access, verify the exact bind address and firewall. |

For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The earlier files used a fixed container name, a machine-specific data path, a required external network and an unused Edge port. The current deployment keeps Portainer away from application networks and documents its privileged host access.

- [Official website](https://www.portainer.io/)
- [Docker installation guide](https://docs.portainer.io/start/install-ce/server/docker/linux)
- [Initial setup](https://docs.portainer.io/start/install-ce/server/setup)
- [Requirements](https://docs.portainer.io/start/requirements-and-prerequisites)
- [Backup settings](https://docs.portainer.io/admin/settings/general)
- [Source repository](https://github.com/portainer/portainer)
- [Container image](https://hub.docker.com/r/portainer/portainer-ce)
- [Release notes](https://github.com/portainer/portainer/releases)
- [License](https://github.com/portainer/portainer/blob/develop/LICENSE)
- [Security policy](https://github.com/portainer/portainer/security/policy)
