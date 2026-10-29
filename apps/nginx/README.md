# nginx

nginx is an HTTP web server and reverse proxy. This deployment provides a small, read-only static-site server with a tracked configuration, a health check and an optional external network for proxying to other containers.

## Supported setup

- Official `nginx:stable-alpine` image channel.
- Static files served from the tracked `html` directory by default, or from an absolute host directory selected in `.env`.
- HTTP bound to the Docker host's loopback address on port `8080` by default.
- Read-only container filesystem with temporary writable cache and runtime directories.
- Optional `stacklab-proxy` network for custom reverse-proxy configurations.

The stable tag currently tracks nginx 1.30.6 and can resolve to a newer stable patch or series when pulled. TLS termination, automatic certificate issuance, Docker service discovery, PHP and other application runtimes are outside the maintained base deployment.

## Before you start

- Install Docker Engine and the Docker Compose plugin (`docker compose`).
- Make sure the selected host port is available.
- Prepare a directory containing the static files you want to publish, or start with the included example page.

The default loopback binding is intended for local access and SSH tunnels. Do not expose a site to an untrusted network until you have designed HTTPS, access control, request limits and firewall rules for that site.

## Quick start

`.env` is optional because the default configuration works without it. From the repository root:

```bash
cd apps/nginx
docker compose config
docker compose up -d
docker compose ps
```

Open <http://localhost:8080>. The page should say that nginx is running. Check the health endpoint separately:

```bash
curl --fail http://127.0.0.1:8080/nginx-health
```

It should print `healthy`.

For a remote Docker host, keep nginx bound to loopback and forward the port through SSH:

```bash
ssh -N -L 8080:127.0.0.1:8080 user@server
```

Then open <http://localhost:8080> on your computer.

## Publish a static site

For a site maintained in this repository, replace the files under `html/`. To serve files stored elsewhere, copy the environment example and set an absolute directory:

```bash
cp .env.example .env
```

```dotenv
NGINX_CONTENT_SOURCE=/srv/www/example
```

Inspect the resolved mount before applying the change:

```bash
docker compose config
docker compose up -d
```

nginx reads the content as UID `101` in the container, although the master process starts as root. Files need only be readable and directories traversable. nginx does not need write permission. Avoid mounting secrets or unrelated parent directories as the document root.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `NGINX_BIND_ADDRESS` | `127.0.0.1` | Host interface accepting HTTP connections |
| `NGINX_HTTP_PORT` | `8080` | HTTP port on the Docker host |
| `NGINX_CONTENT_SOURCE` | `./html` | Read-only static-content directory |
| `NGINX_PROXY_NETWORK` | `stacklab-proxy` | Existing network used only by the proxy-network extension |

Changing the content source does not copy files. Keep the old and new directories until the new site has been verified. A relative source is resolved from this app directory. Use an absolute path for content stored outside the checkout.

The maintained virtual host is in `config/default.conf`. Run the built-in syntax check after editing it:

```bash
docker compose run --rm nginx nginx -t
docker compose up -d
```

The `/nginx-health` location is used by the container health check. Preserve an unauthenticated local response at that path or update the health check together with the configuration.

## Reverse proxy extension

The extension attaches nginx to an existing external network so a custom configuration can refer to upstream containers by service name. Create the network once and start nginx with both files:

```bash
docker network create stacklab-proxy
docker compose -f compose.yaml \
  -f extensions/compose.proxy-network.yaml config
docker compose -f compose.yaml \
  -f extensions/compose.proxy-network.yaml up -d
```

Attach only the application containers nginx must reach to the same network. Then replace or extend `config/default.conf` with a reviewed `proxy_pass` configuration. Use the same two Compose files for `pull`, `logs`, `up` and `down`. Run `down` with both files before disabling the extension.

nginx does not discover Docker services or request certificates automatically. If label-driven routing and automatic ACME are the goal, use the repository's [Traefik deployment](../traefik/README.md). See the [shared reverse-proxy guidance](../../docs/reverse-proxy.md) before publishing applications.

## Your data

The content selected by `NGINX_CONTENT_SOURCE` is the only user data in the base deployment. It is mounted read-only and remains in its host directory when the container is recreated or removed. The nginx configuration and example page are tracked in Git. Cache and PID files live in temporary filesystems and are disposable.

## Back up and restore

Back up the content directory with the filesystem or source-control workflow appropriate for the site. Preserve any changes to `config/default.conf` and `.env` separately if they are not committed. To restore, place the content at its original path or update `NGINX_CONTENT_SOURCE`, run `docker compose config`, start the deployment and request representative files.

There is no Docker-managed application volume to restore. Removing the container does not delete host content.

## Update

Review the nginx release notes, then pull and recreate the container:

```bash
docker compose pull nginx
docker compose up -d
docker compose ps
docker compose logs --tail=100 nginx
```

Run `nginx -t`, request the health endpoint and check representative static files or proxied routes. Because `stable-alpine` is a moving tag, record the resolved image digest before an update when reproducible rollback matters.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| Browser cannot connect | Run `docker compose ps` and confirm `NGINX_HTTP_PORT` is available. Remote clients cannot reach the loopback default without a tunnel. |
| Response is `403 Forbidden` | Ensure the content directory and its parents are traversable and contain a readable index file. |
| Response is `404 Not Found` | Confirm the requested file exists below the resolved `NGINX_CONTENT_SOURCE` and inspect `docker compose config`. |
| Container is unhealthy | Request `/nginx-health`, run `docker compose logs nginx` and validate the configuration with `nginx -t`. |
| Upstream name is not resolved | Start with the proxy-network extension and attach the upstream service to the same external network. |
| Proxied request returns `502` or `504` | Check the upstream service name, container port, protocol, shared network and application logs. |

For general Docker commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The deployment follows the official image's static-content bind-mount pattern and its documented requirements for a read-only root filesystem. Stacklab adds a loopback-only port, explicit temporary write locations, a minimal health endpoint and an optional external proxy network. The Alpine stable variant is intentionally the only supported image here.

- [Official nginx website](https://nginx.org/)
- [nginx documentation](https://nginx.org/en/docs/)
- [Beginner's guide](https://nginx.org/en/docs/beginners_guide.html)
- [Official container image](https://hub.docker.com/_/nginx)
- [Container-image source repository](https://github.com/nginx/docker-nginx)
- [Release news](https://nginx.org/en/news.html)
- [License](https://nginx.org/LICENSE)
- [Community support](https://community.nginx.org/)
- [Security advisories](https://nginx.org/en/security_advisories.html)
