<img src="../../docs/assets/mosquitto/eclipsemosquitto_logo.svg" alt="Eclipse Mosquitto logo" width="150">

# Eclipse Mosquitto

Mosquitto is a lightweight MQTT broker for messaging between sensors, automation systems and other clients. This setup provides one authenticated MQTT listener with durable session and retained-message storage.

## Supported setup

- Official `eclipse-mosquitto:2.1-alpine` image channel.
- Password authentication through Mosquitto 2.1's password-file plugin. Anonymous clients are rejected.
- MQTT over TCP on port `1883`, published to host loopback by default. WebSockets, TLS termination and dynamic security are outside this maintained base.
- Docker-managed persistent data by default, with an optional absolute host path.

The `2.1-alpine` tag receives patch releases when pulled. This documentation was reviewed against Mosquitto 2.1.2.

## Before you start

- Docker Engine and the Docker Compose plugin (`docker compose`).
- An initial username and password, created before the broker starts.
- Port `1883` available on the configured host address.
- Existing users: the legacy file used `/opt/docker/mosquitto` paths and an external `smart-home-net`. The new defaults do not migrate those files or use that network automatically.

MQTT username/password authentication does not encrypt traffic. The loopback default is appropriate for local clients and SSH tunnels. Before allowing LAN or wider access, use a trusted network and design TLS according to the [upstream TLS documentation](https://mosquitto.org/man/mosquitto-tls-7.html). Never publish an unencrypted broker directly to the internet.

## Quick start

`.env` is optional, but a password file is required. From the repository root:

```bash
cd apps/mosquitto

# Prompts securely for the password. The -c option creates or replaces the file.
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD/config:/work" \
  eclipse-mosquitto:2.1-alpine \
  mosquitto_passwd -c /work/passwords stacklab

docker compose up -d
docker compose ps
```

Do not put the password directly on the command line because it may be recorded in shell history. The generated hash file is ignored by Git.

Verify publish and subscribe in an interactive container shell:

```bash
docker compose exec -it mosquitto sh

# Run these inside the container. The password is hidden and is not literal in history.
read -s -p "Password: " MQTT_PASSWORD; echo
mosquitto_pub -h localhost -t stacklab/check -m working -r -u stacklab -P "$MQTT_PASSWORD"
mosquitto_sub -h localhost -t stacklab/check -u stacklab -P "$MQTT_PASSWORD" -C 1
mosquitto_pub -h localhost -t stacklab/check -n -r -u stacklab -P "$MQTT_PASSWORD"
unset MQTT_PASSWORD
exit
```

The subscription should print `working`. The final publish removes the retained test message. The password exists briefly in each client process's arguments. Use a protected client configuration file when stronger local process isolation is required.

## Manage users

Stop the broker before replacing the password file. Add or update a user without `-c`. Using `-c` again erases all existing users.

```bash
docker compose stop mosquitto

docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD/config:/work" \
  eclipse-mosquitto:2.1-alpine \
  mosquitto_passwd /work/passwords another-user

docker compose up -d
```

For many users or role-based topic permissions, evaluate Mosquitto's dynamic-security plugin rather than extending this simple password-file setup indefinitely.

## Configuration

```bash
cp .env.example .env
# Edit .env, inspect the resolved ports and mounts, then apply.
docker compose config
docker compose up -d
```

| Variable | Default | Purpose |
|---|---|---|
| `MOSQUITTO_BIND_ADDRESS` | `127.0.0.1` | Host address accepting MQTT connections |
| `MOSQUITTO_PORT` | `1883` | MQTT port on the Docker host |
| `MOSQUITTO_DATA_SOURCE` | `data` | Named volume or absolute host path for broker persistence |
| `SHARED_NETWORK_NAME` | `stacklab-shared` | Existing network used only by the shared-network extension |

To serve trusted LAN clients, set the bind address to the server's LAN IP instead of every interface. Allow the chosen port through the host firewall. Clients then use that IP and port.

> [!WARNING]
> Changing the data source does not move retained messages or durable sessions. Back up the current deployment and inspect the resolved `/mosquitto/data` mount before recreating it.

Advanced broker behavior belongs in `config/mosquitto.conf`. Validate changes against the current [configuration reference](https://mosquitto.org/man/mosquitto-conf-5.html). An invalid file prevents startup.

## Extensions

The shared-network extension lets other Stacklab Compose projects reach the broker as `mosquitto:1883` without publishing it beyond the host. Follow the [shared extension workflow](../../docs/extensions.md), create the network once, and use the same file for every lifecycle command:

```bash
docker network create stacklab-shared
docker compose -f compose.yaml -f extensions/compose.shared-network.yaml up -d
```

Set `SHARED_NETWORK_NAME` only when all participating projects use another existing network name. Authentication remains required, and traffic on the Docker network is not encrypted.

## Your data

| Source | Container path | Contents | Backup need |
|---|---|---|---|
| `MOSQUITTO_DATA_SOURCE` | `/mosquitto/data` | Retained messages, durable subscriptions and sessions | Essential when those features matter |
| `./config/mosquitto.conf` | `/mosquitto/config/mosquitto.conf` | Tracked broker configuration | Reproducible from Git |
| `./config/passwords` | `/mosquitto/config/passwords` | Generated password hashes | Essential |

The named data volume is retained by `docker compose down`. **`docker compose down -v` deletes it**. Passwords are hashed, but the file is still security-sensitive and must not be committed or shared casually.

## Back up and restore

Follow [the backup and restore guide](docs/backup-and-restore.md). It stops the broker before archiving its persistence database and verifies recovery with a separate Compose project.

## Update

Back up first and read the [release notes](https://mosquitto.org/blog/). Then:

```bash
docker compose pull mosquitto
docker compose up -d
docker compose ps
```

Repeat the authenticated publish/subscribe check and verify retained messages or durable sessions used by your clients. Keep the pre-update backup because persistence formats may be rewritten by a newer broker.

## Troubleshooting

| Symptom | Check / action |
|---|---|
| Broker exits immediately | Read `docker compose logs mosquitto`. Confirm `config/passwords` exists, is readable and the configuration is valid. |
| Connection is refused from another machine | Loopback is the default. Configure the server's LAN address and check its firewall. |
| `Not authorized` appears | Supply a valid username and password. Recreate or update the password file while the broker is stopped. |
| Other containers cannot connect | Enable the same external network for both projects and use `mosquitto:1883`, not `localhost`. |
| Retained messages or sessions disappeared | Check whether the data source or Compose project name changed. Preserve both old and new stores until migration is complete. |

For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The earlier example allowed anonymous access and used a fixed container name, machine-specific `/opt` paths, an always-on WebSocket listener and a required external network. The current files follow the official image layout and Mosquitto 2.1 password-file plugin guidance.

- [Official website](https://mosquitto.org/)
- [Documentation](https://mosquitto.org/documentation/)
- [Configuration reference](https://mosquitto.org/man/mosquitto-conf-5.html)
- [Password-file plugin](https://mosquitto.org/documentation/plugins/password-file/)
- [Official container image](https://hub.docker.com/_/eclipse-mosquitto)
- [Source repository](https://github.com/eclipse-mosquitto/mosquitto)
- [Release notes](https://mosquitto.org/blog/)
- [License](https://github.com/eclipse-mosquitto/mosquitto/blob/master/epl-v20)
- [Security policy](https://github.com/eclipse-mosquitto/mosquitto/security/policy)
