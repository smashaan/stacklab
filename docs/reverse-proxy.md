# Reverse proxy

Many self-hosted applications can be exposed through a reverse proxy such as Caddy, nginx or Traefik. This repository keeps reverse-proxy integration optional so that each deployment remains usable without a particular domain or proxy setup.

## Recommended approach

- Run the reverse proxy as its own deployment.
- Create an external Docker network only for proxy-connected services.
- Attach only services that should be exposed through the proxy.
- Keep internal services, such as databases, off the proxy network.

## Example external network

Create the network once:

```bash
docker network create stacklab-proxy
```

Use it in a reverse-proxy deployment:

```yaml
networks:
  proxy:
    name: stacklab-proxy
    external: true
```

Attach an application to it:

```yaml
services:
  app:
    networks:
      - default
      - proxy

networks:
  default:
  proxy:
    external: true
```

## Security notes

- Do not attach databases to the proxy network unless there is a specific reason.
- Do not publish internal service ports when they are reachable through the proxy.
- Use TLS and authentication for services exposed beyond your local network.
- Review firewall rules before exposing a service to the internet.
