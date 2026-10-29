# Traefik

Traefik is a reverse proxy and load balancer that discovers explicitly enabled Docker services from container labels. This setup provides local HTTP routing, an authenticated dashboard and an optional Let's Encrypt HTTPS extension.

## Supported setup

- Official Traefik Proxy `v3.7.16`, pinned to the current security-patch release.
- Docker provider with `exposedByDefault=false`. A container is ignored unless it has `traefik.enable=true`.
- Dedicated external `stacklab-proxy` network for communication with routed applications.
- HTTP and HTTPS entry points bound to localhost by default.
- Dashboard routed through `api@internal` and protected by bcrypt-backed Basic Authentication. Insecure API mode is disabled.
- Optional Let's Encrypt HTTP-01 extension with persistent certificate state and HTTP-to-HTTPS redirection.

This is a single-host Docker deployment. Swarm, Kubernetes, high availability, DNS challenges and running behind another edge proxy require separate designs.

## Before you start

- Docker Engine and the Docker Compose plugin (`docker compose`).
- Permission to read `/var/run/docker.sock` and create an external Docker network.
- `htpasswd` locally, or Docker access to run the password-generation command below.
- For public TLS: a real DNS name resolving to this host and inbound TCP ports 80 and 443 reaching Traefik.

> [!CAUTION]
> The Docker socket is a high-value host interface. A read-only bind mount prevents ordinary filesystem writes to the socket path, but it does not turn the Docker API into a read-only API. A Traefik compromise could expose host-level Docker access. Keep Traefik patched, route only trusted workloads and consider an authorization-filtering socket proxy when your threat model requires stronger isolation.

## Quick start

`.env` is required for the dashboard credential. Generate a bcrypt record interactively so the password does not appear in the command or shell history:

```bash
cd apps/traefik
cp .env.example .env

docker run --rm -it httpd:2.4-alpine htpasswd -nB admin
```

Copy the complete `admin:$2y$...` output after `TRAEFIK_DASHBOARD_AUTH=` in `.env` and enclose it in single quotes:

```dotenv
TRAEFIK_DASHBOARD_AUTH='admin:$2y$05$replace_with_complete_generated_hash'
```

Create the proxy network once, validate the resolved configuration and start Traefik:

```bash
docker network create stacklab-proxy
docker compose config
docker compose up -d
docker compose ps
```

Open <http://traefik.localhost/dashboard/> and sign in as `admin`. The trailing slash is required. Confirm the dashboard shows the `dashboard@docker` router and no unexpected application routers.

The base deployment uses local HTTP. Do not change the bind address for remote use until HTTPS is configured.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `TRAEFIK_DASHBOARD_AUTH` | Required | Complete `username:bcrypt-hash` Basic Authentication record |
| `TRAEFIK_DASHBOARD_HOST` | `traefik.localhost` | Exact hostname used by the dashboard router |
| `TRAEFIK_BIND_ADDRESS` | `127.0.0.1` | Host interface accepting proxy traffic |
| `TRAEFIK_HTTP_PORT` | `80` | HTTP entry-point port on the Docker host |
| `TRAEFIK_HTTPS_PORT` | `443` | HTTPS entry-point port on the Docker host |
| `TRAEFIK_PROXY_NETWORK` | `stacklab-proxy` | Existing external network shared with routed applications |
| `TRAEFIK_ACME_EMAIL` | Extension only | Let's Encrypt account and expiry-notification email |
| `TRAEFIK_CERTIFICATES_SOURCE` | `certificates` | Named volume or absolute host path for ACME state |

Changing the dashboard hostname requires DNS or hosts-file resolution to the Traefik host. A `*.localhost` name normally resolves to loopback in modern environments. Use `curl --resolve` when testing another name before DNS is ready.

The bcrypt record is visible to Docker administrators through container metadata, though the plaintext password is not. Docker administrators already control the proxy container and socket. Keep `.env` private and use a unique dashboard password.

## Route an application

Traefik and the application must share the proxy network. Add an app-specific extension to the application rather than publishing every container by default. A minimal service addition looks like:

```yaml
services:
  app:
    networks:
      - default
      - proxy
    labels:
      traefik.enable: "true"
      traefik.docker.network: stacklab-proxy
      traefik.http.routers.app.rule: "Host(`app.localhost`)"
      traefik.http.routers.app.entrypoints: web
      traefik.http.services.app.loadbalancer.server.port: "8080"

networks:
  proxy:
    name: stacklab-proxy
    external: true
```

Replace the service name, hostname and internal port. The load-balancer port is the application's container port, not its published host port. Router, middleware and service names must be unique across the Docker provider.

Labels are executable routing configuration controlled by anyone who can deploy a container. Review them like code. Do not attach databases, caches or unrelated internal services to the proxy network.

## Let's Encrypt HTTPS extension

HTTP-01 is appropriate only when the public hostname resolves to this host and Let's Encrypt can reach port 80. Set a real dashboard hostname, account email and public bind address in `.env`:

```dotenv
TRAEFIK_DASHBOARD_HOST=traefik.example.com
TRAEFIK_BIND_ADDRESS=0.0.0.0
TRAEFIK_ACME_EMAIL=admin@example.com
```

Then validate and start with the extension:

```bash
docker compose -f compose.yaml \
  -f extensions/compose.letsencrypt.yaml config

docker compose -f compose.yaml \
  -f extensions/compose.letsencrypt.yaml up -d
```

The extension redirects HTTP to HTTPS, obtains the dashboard certificate through the `letsencrypt` resolver and stores ACME state under `/letsencrypt`. Application HTTPS routers must select `websecure`, enable TLS and reference the same resolver:

```yaml
labels:
  traefik.http.routers.app.entrypoints: websecure
  traefik.http.routers.app.tls: "true"
  traefik.http.routers.app.tls.certresolver: letsencrypt
```

Use the same two Compose files for `pull`, `logs`, `up` and `down`. Test certificate configuration against Let's Encrypt staging before requesting many production certificates because rate limits apply. Wildcards and hosts that cannot expose port 80 need a DNS challenge and provider credentials, which are outside this generic extension.

## Your data

The base deployment is stateless: static configuration is tracked in Git, dynamic Docker routes come from application labels, and the dashboard credential comes from `.env`.

With the Let's Encrypt extension, `TRAEFIK_CERTIFICATES_SOURCE` contains the ACME account, private keys and certificates. It is sensitive and must be backed up. Named storage survives `docker compose down`. **`docker compose down -v` deletes it** when the extension is included.

> [!WARNING]
> Changing the certificate source does not copy ACME state. An empty source creates a new account and can trigger duplicate issuance or rate limits. Back up first and inspect the resolved `/letsencrypt` mount with the full `docker compose ... config` command.

Access logs can contain client addresses, requested URLs and other operational metadata. Docker's logging driver controls retention. Set host-level rotation appropriate to your privacy and capacity requirements.

## Back up and restore

For the base deployment, preserve `.env` securely. Everything else is reproducible from Git and application labels. When using Let's Encrypt, follow the [certificate-state backup and restore guide](docs/backup-and-restore.md).

## Update

Review the [release notes](https://github.com/traefik/traefik/releases) and migration guidance before changing the exact image tag. Back up ACME state when enabled, then use the same Compose files as the running deployment:

```bash
docker compose pull traefik
docker compose up -d
docker compose ps
docker compose logs --tail=100 traefik
```

Verify dashboard authentication, HTTP-to-HTTPS behavior, certificate validity, WebSockets and representative application routes. Restore the previous image and matching configuration if rollback is required.

## Recovery and troubleshooting

| Symptom | Check / action |
|---|---|
| Compose reports a missing dashboard credential | Generate the bcrypt record, keep the complete value single-quoted in `.env`, and rerun `docker compose config`. |
| External network is missing | Run `docker network create stacklab-proxy`, or use the same custom `TRAEFIK_PROXY_NETWORK` in Traefik and every routed app. |
| Dashboard returns `404` | Use the exact configured hostname and the `/dashboard/` trailing slash. An IP URL does not match a Host rule. |
| Application returns `404` | Check `traefik.enable`, router rule, entry point and shared proxy network in the dashboard. |
| Application returns `502` or `504` | Confirm Traefik shares the selected network and the service label uses the container's listening port. |
| Certificate is not issued | Check public DNS, inbound ports 80/443, ACME email, router resolver label and Traefik logs. Avoid repeated production retries. |
| Ports 80 or 443 are allocated | Stop the conflicting listener or change the host ports for local testing. Public HTTP-01 normally requires external port 80. |
| Docker provider fails | Verify the real `/var/run/docker.sock` exists and review permissions. Do not expose an unauthenticated Docker TCP endpoint. |

For shared design guidance, see [reverse proxy documentation](../../docs/reverse-proxy.md). For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The earlier files used a moving tag, an unauthenticated API and an invalid socket path. The current deployment follows Traefik's Docker-provider model, requires explicit exposure labels and keeps public ACME settings separate from local HTTP use.

- [Official website](https://traefik.io/traefik/)
- [Traefik documentation](https://doc.traefik.io/traefik/)
- [Docker provider](https://doc.traefik.io/traefik/providers/docker/)
- [API and dashboard security](https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/)
- [ACME documentation](https://doc.traefik.io/traefik/https/acme/)
- [Source repository](https://github.com/traefik/traefik)
- [Container image](https://hub.docker.com/_/traefik)
- [Release notes](https://github.com/traefik/traefik/releases)
- [Support lifecycle](https://doc.traefik.io/traefik/deprecation/releases/)
- [License](https://github.com/traefik/traefik/blob/master/LICENSE.md)
- [Security policy](https://github.com/traefik/traefik/security/policy)
