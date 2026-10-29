# SFTPGo

Share files through SFTP and a browser with managed users, permissions and quotas. This app runs the SFTPGo Community edition with its built-in WebAdmin, WebClient and SQLite database.

## Supported setup

- SFTPGo Community `v2.7.6` using the standard upstream image
- Docker-managed named volumes for configuration, user files and SSH host keys
- Web and SFTP access bound to localhost by default
- Local filesystem storage and the built-in SQLite data provider

Cloud storage, external databases, FTP, WebDAV and high-availability deployments are outside this repository's supported configuration. See the [SFTPGo documentation](https://docs.sftpgo.com/) for those options.

## Before you start

- Install Docker Engine and the Docker Compose plugin (`docker compose`).
- Choose which trusted devices should reach the SFTP service. Keep the default loopback binding for local testing or change it to the server's LAN address after creating an administrator and user.
- If you use host directories, make them writable by UID and GID `1000`, which the upstream container uses by default.

## Quick start

`.env` is optional. The defaults work without it and keep both interfaces on the Docker host.

From the repository root:

```bash
cd apps/sftpgo
docker compose up -d
docker compose ps
```

Open <http://localhost:8080/web/admin> and create the first administrator. Add a user, give it a password or public key, and assign only the permissions it needs.

Test SFTP from the Docker host, replacing `username` with the user you created:

```bash
sftp -P 2022 username@127.0.0.1
```

Upload a disposable file, download it again, and confirm that it also appears in the user's WebClient. The WebClient is available at <http://localhost:8080/web/client>.

For a remote Docker host, reach WebAdmin through an SSH tunnel:

```bash
ssh -N -L 8080:127.0.0.1:8080 user@server
```

Then open the same localhost WebAdmin address on your computer.

## Configuration

Copy the example only when you need to change ports, network bindings or storage locations:

```bash
cp .env.example .env
# Edit .env, then inspect and apply the configuration.
docker compose config
docker compose up -d
```

| Variable | Default | Purpose |
|---|---|---|
| `SFTPGO_WEB_BIND_ADDRESS` | `127.0.0.1` | Host interface for WebAdmin and WebClient |
| `SFTPGO_WEB_PORT` | `8080` | Web port on the Docker host |
| `SFTPGO_SFTP_BIND_ADDRESS` | `127.0.0.1` | Host interface for SFTP connections |
| `SFTPGO_SFTP_PORT` | `2022` | SFTP port on the Docker host |
| `SFTPGO_DATA_SOURCE` | `data` | Named volume or absolute host path for the database and shared files |
| `SFTPGO_HOME_SOURCE` | `home` | Named volume or absolute host path for working data and SSH host keys |

To accept SFTP connections from your LAN, set `SFTPGO_SFTP_BIND_ADDRESS` to the server's LAN IP. Clients then connect to that address on port `2022`. Avoid `0.0.0.0` unless every host interface is meant to accept connections. Do not expose WebAdmin or SFTP directly to the public internet without a separate security review, firewall rules and a tested update process.

SFTPGo manages users inside WebAdmin. Prefer public-key authentication where practical, use strong unique passwords otherwise, and disable accounts that are no longer needed. Product settings changed through WebAdmin are stored in the data volume.

## Your data

| Source variable | Default volume | Container path | Contents |
|---|---|---|---|
| `SFTPGO_DATA_SOURCE` | `data` | `/srv/sftpgo` | SQLite database, user files and SFTPGo backups |
| `SFTPGO_HOME_SOURCE` | `home` | `/var/lib/sftpgo` | Working data, configuration additions and SSH host keys |

Back up both sources together. Losing the home volume changes the server's SSH host identity, which causes clients to report a host-key mismatch. Losing the data volume loses locally stored accounts, settings and user files.

Named volumes keep runtime data outside the checkout but do not encrypt it. `docker compose down` keeps the volumes. **`docker compose down -v` deletes them.**

Host directories are useful when other processes on the Docker host must access shared files. Create them outside the repository and grant UID and GID `1000` the required access. Changing a source does not copy existing data. Inspect the resolved mounts and migrate or restore the existing contents before recreating a deployment with new sources.

## Back up and restore

Follow the [backup and restore guide](docs/backup-and-restore.md). It stops the app for a consistent copy of the SQLite database, files and SSH host keys, then verifies the restore in a separate Compose project.

## Update

Read the [release notes](https://github.com/drakkan/sftpgo/releases), back up both persistent sources, and update the image tag in `compose.yaml` after reviewing the target release.

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Sign in to WebAdmin, connect with SFTP and transfer a disposable file. Confirm that existing users and files remain available and that clients accept the same SSH host key.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| WebAdmin does not open from another computer | It is bound to loopback by default. Use the SSH tunnel or bind it to a trusted address. |
| SFTP works locally but not from the LAN | Set `SFTPGO_SFTP_BIND_ADDRESS` to the server's LAN IP and allow the selected port through the host firewall. |
| A host directory is not writable | Check ownership and permissions. The container runs as UID and GID `1000` by default. |
| The client reports a changed host key | Confirm that the original home volume is mounted. Do not accept a new key until the cause is understood. |
| The container exits or restarts | Run `docker compose logs --tail=100 sftpgo` and check for storage permissions or port conflicts. |

For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

This deployment follows the upstream Docker layout and preserves both documented storage locations. Stacklab adds loopback defaults and configurable storage sources. It does not build or maintain a replacement image.

- [Official website](https://sftpgo.com/)
- [Documentation](https://docs.sftpgo.com/)
- [Docker guide](https://docs.sftpgo.com/latest/docker/)
- [Source repository](https://github.com/drakkan/sftpgo)
- [Container image](https://hub.docker.com/r/drakkan/sftpgo)
- [Release notes](https://github.com/drakkan/sftpgo/releases)
- [License](https://github.com/drakkan/sftpgo/blob/main/LICENSE)
- [Community support](https://github.com/drakkan/sftpgo/discussions)
- [Security policy](https://github.com/drakkan/sftpgo/security/policy)
