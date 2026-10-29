# Stirling PDF backup and restore

Run these commands on the Docker host from `apps/stirling-pdf/`, using the same Compose project as the application. The backup copies data through the container, so it works with named volumes and documented host paths. The restore uses fresh named volumes to avoid writing into original host directories. External databases require their own consistent backup. Test this guide with disposable data before relying on it.

## Back up

Finish active jobs first. The application will be unavailable while stopped.
Use a new backup directory outside this repository. The example uses your home
directory. Choose a protected backup destination with enough space.

Run the whole block together. It uses a subshell so a failed command stops the
backup without closing your interactive terminal:

```bash
(
  set -eu
  umask 077
  BACKUP_DIR="$HOME/stacklab-backups/stirling-pdf/$(date -u +%Y%m%dT%H%M%SZ)"
  mkdir -p "$BACKUP_DIR"
  cp compose.yaml "$BACKUP_DIR/compose.yaml"
  if [ -f .env ]; then cp .env "$BACKUP_DIR/.env"; fi
  docker compose -f compose.yaml config --images > "$BACKUP_DIR/images.txt"
  IMAGE_ID="$(docker compose -f compose.yaml images -q stirling-pdf)"
  docker image inspect "$IMAGE_ID" --format '{{index .RepoDigests 0}}' \
    > "$BACKUP_DIR/image-digest.txt"
  docker image inspect "$IMAGE_ID" > "$BACKUP_DIR/image-inspect.json"
  docker compose -f compose.yaml stop stirling-pdf
  for directory in configs storage customFiles pipeline tessdata logs; do
    docker compose -f compose.yaml cp "stirling-pdf:/$directory" - > "$BACKUP_DIR/$directory.tar"
    tar -tf "$BACKUP_DIR/$directory.tar" > /dev/null
  done
  docker compose -f compose.yaml start stirling-pdf
  printf 'Backup directory: %s\n' "$BACKUP_DIR"
)
```

`docker compose cp` streams each directory as a tar archive. No helper image or knowledge of Docker's volume storage path is needed. The archives preserve the files' ownership metadata. If a command fails after stopping the service, inspect the error and run `docker compose -f compose.yaml start stirling-pdf` to resume it. A partial backup is not a successful backup. Checking an archive's format does not establish that the application will restore correctly.

Keep the backup private because it contains documents, account data, keys and possibly `.env` secrets. Copy completed backups off the host as well. The saved Compose file and image digest record what was running. Because the Compose file follows a moving stable tag, recreate an exact older environment by replacing its image with the value saved in `image-digest.txt`.

## Restore into a separate deployment

Review `image-digest.txt` before restoring. The saved Compose file uses a moving stable tag, so replace its image with that recorded digest when an exact-version restore is required. Set `BACKUP_DIR` to the completed backup directory. This example creates a new working directory and project and binds port 18080 to loopback. Ensure that port is free. The existing project's volumes remain untouched.

```bash
(
  set -eu
  umask 077
  BACKUP_DIR="/absolute/path/to/completed/backup"
  RESTORE_PROJECT="stirling-restore-$(date -u +%Y%m%d%H%M%S)"
  RESTORE_DIR="$HOME/stacklab-restores/$RESTORE_PROJECT"
  mkdir -p "$RESTORE_DIR"
  cp "$BACKUP_DIR/compose.yaml" "$RESTORE_DIR/compose.yaml"
  cd "$RESTORE_DIR"
  export STIRLING_PDF_PORT=18080
  export STIRLING_PDF_BIND_ADDRESS=127.0.0.1
  docker compose -f compose.yaml -p "$RESTORE_PROJECT" create stirling-pdf
  for directory in configs storage customFiles pipeline tessdata logs; do
    tar -tf "$BACKUP_DIR/$directory.tar" > /dev/null
    docker compose -f compose.yaml -p "$RESTORE_PROJECT" cp --archive - stirling-pdf:/ < "$BACKUP_DIR/$directory.tar"
  done
  docker compose -f compose.yaml -p "$RESTORE_PROJECT" up -d
  docker compose -f compose.yaml -p "$RESTORE_PROJECT" ps
  printf 'Restore directory: %s\nProject: %s\n' "$RESTORE_DIR" "$RESTORE_PROJECT"
)
```

At <http://localhost:18080>, sign in with an existing account and confirm saved
files and settings. Process a disposable PDF and open the result. Use an SSH
tunnel for a remote host, forwarding port 18080 instead of 8080.

The restore does not copy the saved `.env` into the test deployment. This keeps
the restore isolated on new named volumes. Review the saved `.env` separately
when rebuilding the original storage layout.

Record the printed project name and directory. To stop the test deployment, run
`docker compose -p PROJECT_NAME stop` from that directory. Future Compose commands
must use that same project name and the same port/bind settings. Do not delete
the original data until recovery has been verified and cutover is complete.

## Migrating the previous bind-mount setup

This guide's restore commands target the new named-volume configuration. Do not
use them blindly with the old bind-mount Compose file: it can point a supposedly
separate project at the original host directories.

Before replacing an existing deployment, retain its old Compose file and `.env`,
record the actual application version running, finish jobs and stop it. Back up
its entire data directory (`./stirling-data` or the old `STIRLING_BASE_DIR`) to a
location outside this repository, preserving ownership. Keep that original copy.

Prepare a separate deployment using the new named-volume Compose file and the
same application image version. Copy each old directory into its matching mount
using `docker compose cp --archive`, preserving numeric ownership. The mappings
are listed in the [README](../README.md#your-data). Start and verify the migrated
copy before switching users to it. Upgrade the application as a separate step.
If the old image version cannot be determined, resolve that before migration.

This repository update only changes configuration. It does not migrate files or
remove the old containers, directories or volumes.

## References

- [Docker Compose copy command](https://docs.docker.com/reference/cli/docker/compose/cp/)
- [Upstream operational guidance](https://docs.stirlingpdf.com/Server/Production/)
