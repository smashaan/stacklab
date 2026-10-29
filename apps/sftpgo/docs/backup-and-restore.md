# SFTPGo backup and restore

This procedure creates a stopped-container backup of the SFTPGo database, local user files, working data and SSH host keys. It works with the default named volumes and supported absolute host paths.

## Create a backup

Choose a location outside the repository with enough free space for all user files. The example uses `/srv/backups/sftpgo`.

From `apps/sftpgo`:

```bash
docker compose config --quiet
docker compose stop
sudo mkdir -p /srv/backups/sftpgo
```

Inspect the resolved mount sources:

```bash
docker compose config
docker inspect "$(docker compose ps -aq sftpgo)"
```

The stopped container remains available to `docker inspect`. Copy both resolved sources into the backup location. For named volumes, replace `STACKLAB_SFTPGO_DATA_VOLUME` and `STACKLAB_SFTPGO_HOME_VOLUME` with the names shown by Docker:

```bash
docker run --rm \
  -v STACKLAB_SFTPGO_DATA_VOLUME:/source:ro \
  -v /srv/backups/sftpgo:/backup \
  alpine:3.22 tar -C /source -czf /backup/data.tar.gz .

docker run --rm \
  -v STACKLAB_SFTPGO_HOME_VOLUME:/source:ro \
  -v /srv/backups/sftpgo:/backup \
  alpine:3.22 tar -C /source -czf /backup/home.tar.gz .
```

When a source is an absolute host path, archive that directory with the host's backup tool instead. Preserve numeric ownership, permissions and timestamps.

Record the image reference and checksums beside the archives:

```bash
docker compose images
sha256sum /srv/backups/sftpgo/data.tar.gz /srv/backups/sftpgo/home.tar.gz
docker compose start
```

Confirm that WebAdmin opens and an existing user can transfer a disposable file. Store a copy of the backup on another system.

## Restore safely

Do not overwrite the only copy of a working deployment while testing a restore. Create empty host directories outside the repository:

```bash
sudo mkdir -p /srv/restore/sftpgo/data /srv/restore/sftpgo/home
```

Restore each archive:

```bash
docker run --rm \
  -v /srv/restore/sftpgo/data:/target \
  -v /srv/backups/sftpgo:/backup:ro \
  alpine:3.22 tar -C /target -xzf /backup/data.tar.gz

docker run --rm \
  -v /srv/restore/sftpgo/home:/target \
  -v /srv/backups/sftpgo:/backup:ro \
  alpine:3.22 tar -C /target -xzf /backup/home.tar.gz

sudo chown -R 1000:1000 /srv/restore/sftpgo/data /srv/restore/sftpgo/home
```

Copy `.env.example` to `.env.restore` and set these sources:

```env
SFTPGO_DATA_SOURCE=/srv/restore/sftpgo/data
SFTPGO_HOME_SOURCE=/srv/restore/sftpgo/home
SFTPGO_WEB_PORT=18080
SFTPGO_SFTP_PORT=12022
```

Start an isolated project with the restored data:

```bash
docker compose --project-name sftpgo-restore --env-file .env.restore up -d
docker compose --project-name sftpgo-restore --env-file .env.restore ps
```

Open <http://localhost:18080/web/admin>, sign in with an existing administrator and connect an existing SFTP user to port `12022`. Verify users, permissions and files. Compare the SSH host-key fingerprint with the original deployment.

Remove the temporary containers after the check:

```bash
docker compose --project-name sftpgo-restore --env-file .env.restore down
```

The restored directories remain after the containers are removed. Keep them until the recovery has been accepted. `.env.restore` can contain host-specific information and must not be committed.
