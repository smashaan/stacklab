# Appsmith backup and restore

Run these commands on the Docker host from `apps/appsmith/`. This procedure uses Appsmith's supported `appsmithctl` archive, which includes the bundled MongoDB database, Appsmith configuration and Git data. It does not cover external services added outside this maintained deployment.

Test this procedure with disposable data before relying on it for recovery.

## Back up

Ensure at least 2 GB of free space in addition to the expected archive size. Finish important edits and confirm that the instance is healthy. Start the interactive encrypted backup:

```bash
docker compose exec appsmith appsmithctl backup
```

Enter a strong, unique archive password and store it separately. Appsmith writes the encrypted archive under `/appsmith-stacks/data/backup/`. List the generated files:

```bash
docker compose exec appsmith \
  sh -c 'ls -lh /appsmith-stacks/data/backup/'
```

Copy the new archive to a protected directory outside this repository, replacing the filename with the generated name:

```bash
mkdir -p "$HOME/stacklab-backups/appsmith"
docker compose cp \
  appsmith:/appsmith-stacks/data/backup/appsmith-backup-TIMESTAMP.tar.gz.enc \
  "$HOME/stacklab-backups/appsmith/"
```

Also copy `compose.yaml` and `.env` when present so the storage and port configuration can be reconstructed. Keep another copy off the Docker host. The archive contains the database, configuration, Git data and encryption keys. Its password protects stored datasource credentials.

Do not use `appsmithctl backup --non-interactive` without reviewing the [upstream warning](https://docs.appsmith.com/getting-started/setup/instance-management/backup-and-restore/backup-instance): non-interactive backups are unencrypted and require the source instance's encryption password and salt during restore.

## Restore into a separate deployment

Use the same Appsmith image version that created the archive unless upstream documents a compatible alternative. This example creates a fresh Compose project with separate named storage and loopback ports 18080 and 18443. Set `BACKUP_FILE` to the encrypted archive's absolute host path.

```bash
(
  set -eu
  umask 077
  BACKUP_FILE="/absolute/path/to/appsmith-backup-TIMESTAMP.tar.gz.enc"
  RESTORE_PROJECT="appsmith-restore-$(date -u +%Y%m%d%H%M%S)"
  RESTORE_DIR="$HOME/stacklab-restores/$RESTORE_PROJECT"
  mkdir -p "$RESTORE_DIR"
  cp compose.yaml "$RESTORE_DIR/compose.yaml"
  cd "$RESTORE_DIR"
  export APPSMITH_HTTP_PORT=18080
  export APPSMITH_HTTPS_PORT=18443
  docker compose -p "$RESTORE_PROJECT" up -d
  docker compose -p "$RESTORE_PROJECT" cp \
    "$BACKUP_FILE" appsmith:/appsmith-stacks/data/backup/
  printf 'Restore directory: %s\nProject: %s\n' "$RESTORE_DIR" "$RESTORE_PROJECT"
)
```

Wait until the separate container is healthy. From the printed restore directory, run the interactive restore with the printed project name:

```bash
export APPSMITH_HTTP_PORT=18080
export APPSMITH_HTTPS_PORT=18443
docker compose -p PROJECT_NAME exec appsmith appsmithctl restore
```

Select the copied archive and enter its password. At <http://localhost:18080>, sign in with an account from the backup. Open an application in edit and published views, exercise a safe datasource query, and confirm configuration and Git-connected applications where applicable.

Record the project name, restore directory, ports and archive used. Future Compose commands for this test must use the same values. Stop the verified restore deployment with:

```bash
export APPSMITH_HTTP_PORT=18080
export APPSMITH_HTTPS_PORT=18443
docker compose -p PROJECT_NAME down
```

This keeps the restore volume for further inspection. Delete it with `down -v` only after identifying the exact test project and confirming that its data is no longer needed. Never delete the original deployment or backup until recovery is verified.

## References

- [Back up an Appsmith instance](https://docs.appsmith.com/getting-started/setup/instance-management/backup-and-restore/backup-instance)
- [Restore an Appsmith instance](https://docs.appsmith.com/getting-started/setup/instance-management/backup-and-restore/restore-instance)
- [`appsmithctl` reference](https://docs.appsmith.com/getting-started/setup/instance-management/appsmithctl)
