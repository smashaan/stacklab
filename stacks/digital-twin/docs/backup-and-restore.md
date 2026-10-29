# Digital twin backup and restore

A complete recovery set contains a PostgreSQL custom-format dump, the matching `.env` and a record of the resolved images. The dump contains accounts, password hashes, inventory and telemetry. Encrypt it and keep an off-host copy.

## Back up

From `stacks/digital-twin`:

```bash
mkdir -p backups
docker compose ps

docker compose exec -T database sh -c \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' \
  > backups/digital-twin.dump

cp -p .env backups/environment
docker compose images

docker compose exec -T database pg_restore --list \
  < backups/digital-twin.dump
```

Confirm the dump is non-empty. `pg_restore --list` checks archive readability but does not replace a restore test.

## Restore test

Use an empty database source, separate Compose project and unused host port:

1. Copy this stack directory to a disposable location and restore `backups/environment` as `.env`.
2. Set `DIGITAL_TWIN_PORT=13000` and `DIGITAL_TWIN_DB_SOURCE` to an empty absolute directory.
3. Start only PostgreSQL and wait for it to become healthy:

   ```bash
   docker compose -p digital-twin-restore up -d database
   docker compose -p digital-twin-restore ps
   ```

4. Restore the database:

   ```bash
   docker compose -p digital-twin-restore exec -T database sh -c \
     'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists' \
     < backups/digital-twin.dump
   ```

5. Start the application:

   ```bash
   docker compose -p digital-twin-restore up -d
   docker compose -p digital-twin-restore ps
   ```

6. Sign in through port `13000` and verify inventory totals, representative devices, relationships and telemetry. Add a disposable record, restart the stack and confirm persistence.
7. Stop the isolated project, record the result and securely remove the disposable database copy.

For real recovery, restore into an empty source using compatible image versions. Preserve the failed source unchanged until the recovered application passes checks. If restoring across PostgreSQL major versions, review the applicable [upgrade documentation](https://www.postgresql.org/docs/18/upgrading.html) first.
