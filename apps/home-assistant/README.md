<img src="../../docs/assets/home-assistant/home-assistant_logo.svg" alt="Home Assistant logo" width="150">

# Home Assistant

Home Assistant is a local home-automation platform for connecting devices, building automations and controlling a smart home. This setup runs Home Assistant Container. It does not include the Supervisor or Home Assistant apps and add-ons.

## Supported setup

- Official `stable` image. Home Assistant OS and pre-release channels are outside this repository's scope.
- Docker-managed `config` volume by default, or an absolute host path configured through `.env`.
- Host networking for local discovery. Home Assistant normally listens on the Docker host's port `8123`. Compose cannot restrict that port to loopback.
- Privileged mode, matching upstream's Container example. Bluetooth D-Bus and host-device access are optional extensions.

The moving `stable` tag can change when pulled. This documentation was last reviewed against Home Assistant 2026.10.4. Upstream recommends Home Assistant OS for most users. Choose Container when you want to manage Docker, companion services, updates and backups yourself.

## Before you start

- Docker Engine 23.0.0 or newer and the Docker Compose plugin. Upstream does not support Docker Desktop for this installation.
- A Linux host with a supported 64-bit architecture and port `8123` available.
- Appropriate host firewall rules before startup.
- Existing Stacklab users: the legacy file used `/opt/docker/homeassistant/config`. Set `HOME_ASSISTANT_CONFIG_SOURCE` to that path before recreating the container, or migrate it before switching. The default named volume starts empty.

This service uses host networking and privileged mode, so it can interact broadly with the host and LAN. Use trusted images and integrations, keep the host patched, and never expose port `8123` directly to the public internet.

## Quick start

`.env` is optional. Defaults use UTC and Docker-managed storage.

```bash
cd apps/home-assistant
docker compose up -d
docker compose ps
```

Open `http://DOCKER-HOST-IP:8123` and complete onboarding. As a persistence check, create a toggle under **Settings > Devices & services > Helpers**, change its state, restart the container and confirm the state remains.

## Configuration

```bash
cp .env.example .env
# Edit .env, inspect the result, then apply it.
docker compose config
docker compose up -d
```

| Variable | Default | Purpose |
|---|---|---|
| `HOME_ASSISTANT_TIME_ZONE` | `Etc/UTC` | Container time zone, using an IANA name |
| `HOME_ASSISTANT_CONFIG_SOURCE` | `config` | Named volume or absolute host path mounted at `/config` |
| `HOME_ASSISTANT_DEVICE` | None | Host path required only by the device extension |

> [!WARNING]
> Changing the configuration source does not move data. An empty source produces a new installation. Back up the current deployment and inspect the resolved mount before recreating it.

Host networking bypasses Compose port publishing. Other computers and containers normally use `http://DOCKER-HOST-IP:8123`. This service cannot also join a user-defined bridge network. Use a firewall, VPN or secured reverse proxy for access beyond a trusted LAN.

## Extensions

See the [shared extension workflow](../../docs/extensions.md).

| Extension | Purpose | Prerequisite |
|---|---|---|
| `compose.bluetooth.yaml` | Mount the host D-Bus socket for Bluetooth | Linux host with D-Bus and Bluetooth hardware |
| `compose.device.yaml` | Pass one serial or other host device through | Set `HOME_ASSISTANT_DEVICE` to an existing absolute path |

```bash
# Bluetooth
docker compose -f compose.yaml -f extensions/compose.bluetooth.yaml up -d

# For a serial or other device, first set HOME_ASSISTANT_DEVICE in .env
docker compose -f compose.yaml -f extensions/compose.device.yaml up -d
```

Both extension files may be supplied together. Prefer `/dev/serial/by-id/...` because `/dev/ttyUSB0` can change after reboot.

## Your data

| Source | Container path | Contents | Backup need |
|---|---|---|---|
| `HOME_ASSISTANT_CONFIG_SOURCE` | `/config` | Configuration, credentials, automations, integrations, database and local backups | Essential |
| `/etc/localtime` | `/etc/localtime` | Read-only host time data | None |
| `/run/dbus` (optional) | `/run/dbus` | Read-only host D-Bus socket | None |

Named volumes keep data outside the checkout but do not encrypt it. `docker compose down` preserves them. **`docker compose down -v` deletes the named configuration volume**.

## Back up and restore

Follow the [backup and restore guide](docs/backup-and-restore.md). Home Assistant Container supports encrypted backups through its interface. Store both the downloaded archive and encryption key away from the Docker host.

## Update

Create and download a backup, then read the [release notes](https://github.com/home-assistant/core/releases), especially backward-incompatible changes.

```bash
docker compose pull homeassistant
docker compose up -d
docker compose ps
```

Repeat the persistence check and test important integrations and automations. Record the resolved image before updating. After a migration, restore a backup made with the older version instead of assuming that pulling an older image reverses data changes.

## Troubleshooting

| Symptom | Check / action |
|---|---|
| Browser cannot connect | Use the host IP and port `8123`. Inspect logs, port use and firewall rules. |
| Network discovery fails | Confirm multicast and same-network reachability. Host networking is already enabled. |
| Bluetooth is unavailable | Use the Bluetooth extension and confirm `/run/dbus` exists. |
| USB adapter changes name | Use `/dev/serial/by-id/...`, verify the path and recreate with the device extension. |
| Empty onboarding appears | Stop and inspect the resolved `/config` source with `docker compose config`. Data is not moved automatically. |

For diagnostic commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The deployment starts from the official Linux Container example. It removes the fixed container name and makes Bluetooth and device access optional. Named storage, host-specific variables and migration guidance are included. The 60-second shutdown grace period lets the default SQLite database close cleanly.

- [Official website](https://www.home-assistant.io/)
- [Container installation](https://www.home-assistant.io/installation/linux/)
- [Container operations](https://www.home-assistant.io/common-tasks/container/)
- [Backup documentation](https://www.home-assistant.io/common-tasks/general/backups/)
- [Source repository](https://github.com/home-assistant/core)
- [Container image](https://github.com/home-assistant/core/pkgs/container/home-assistant)
- [Release notes](https://github.com/home-assistant/core/releases)
- [License](https://github.com/home-assistant/core/blob/dev/LICENSE.md)
- [Community support](https://www.home-assistant.io/help/)
- [Security policy](https://www.home-assistant.io/security/)
