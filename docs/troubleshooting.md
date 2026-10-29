# Shared troubleshooting

Run these commands from the relevant app directory. Replace `app` with the Compose service name shown in that deployment's `compose.yaml`.

## Check deployment status

```bash
docker compose ps
```

## View logs

```bash
docker compose logs -f
docker compose logs -f app
```

## Validate configuration

```bash
docker compose config
```

## Restart a deployment

```bash
docker compose restart
```

## Recreate containers after configuration changes

```bash
docker compose up -d
```

## Stop and remove containers

```bash
docker compose down
```

This does not remove named volumes by default.

## Remove containers and named volumes

> [!WARNING]
> This deletes persistent data managed by the deployment's named volumes.

```bash
docker compose down -v
```

## Common problems

### Port already in use

Change the host port in `.env`, or stop the conflicting service.

### Container keeps restarting

Check logs and validate environment variables:

```bash
docker compose logs app
docker compose config
```

### Cannot connect two services

Within one Compose project, use the target service name as the hostname. Separate app projects require a documented shared-network extension in both deployments. See [Compose extensions and shared networking](extensions.md). Do not use container IP addresses because they can change when containers are recreated.

### Data disappeared after `docker compose down -v`

Named volumes were removed. Always confirm the consequences before using `-v`. Restore the affected data from a tested backup. If no backup exists, stop making changes and preserve any remaining bind-mounted or external data before investigating further.
