# Nextcloud backup and restore

A complete recovery set contains the MariaDB dump, the entire `/var/www/html` tree and the matching `.env`. Keep these artifacts together and encrypted.

## Back up

From `apps/nextcloud`, enable maintenance mode before copying application files:

```bash
mkdir -p backups
docker compose exec --user www-data app php occ maintenance:mode --on

docker compose exec -T db sh -c \
  'mariadb-dump --single-transaction -u root -p"$MARIADB_ROOT_PASSWORD" "$MARIADB_DATABASE"' \
  > backups/nextcloud.sql

docker compose run --rm --no-deps --entrypoint tar app \
  -czf - -C /var/www/html . > backups/nextcloud-html.tar.gz

cp -p .env backups/environment
docker compose exec --user www-data app php occ maintenance:mode --off
docker compose images
```

Confirm maintenance mode is disabled even if a backup command fails. Store the backup off-host with restricted access and record the resolved Nextcloud, MariaDB and Redis image versions.

## Restore test

Use empty host directories and a separate project with an unused port.

1. Copy this app directory to a disposable location and restore `environment` as `.env`.
2. Set `NEXTCLOUD_PORT=18080`, then set both source variables to separate empty absolute directories.
3. Extract `nextcloud-html.tar.gz` into the application directory and preserve its ownership and permissions.
4. Start only MariaDB and Redis, wait for database health, and import the dump:

   ```bash
   docker compose -p nextcloud-restore up -d db redis
   docker compose -p nextcloud-restore exec -T db sh -c \
     'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" "$MARIADB_DATABASE"' \
     < backups/nextcloud.sql
   ```

5. Start the remaining services:

   ```bash
   docker compose -p nextcloud-restore up -d
   docker compose -p nextcloud-restore exec --user www-data app php occ maintenance:mode --off
   docker compose -p nextcloud-restore exec --user www-data app php occ status
   ```

6. Sign in through port `18080`. Download representative files, inspect sharing metadata and confirm cron runs.
7. Stop with `docker compose -p nextcloud-restore down`. Retain the report and securely remove the disposable sensitive copy when finished.

For a real recovery, keep damaged sources unchanged until the restored instance passes checks. Use compatible image versions and follow the [official backup](https://docs.nextcloud.com/server/stable/admin_manual/maintenance/backup.html) and [restore](https://docs.nextcloud.com/server/stable/admin_manual/maintenance/restore.html) requirements when they differ from this guide.
