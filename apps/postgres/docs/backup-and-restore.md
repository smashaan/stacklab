# PostgreSQL backup and restore

This procedure creates a logical, custom-format dump of the configured database. It supports selective inspection and restore with `pg_restore`, and avoids treating a live copy of the database files as a valid backup.

The dump does not automatically include other databases or cluster-wide objects such as additional roles and tablespaces. If you create them, add a dump for every database and use `pg_dumpall --globals-only` for the required global objects. Store those artifacts together and test their complete restore order.

## Back up

From `apps/postgres`, confirm PostgreSQL is healthy and create the dump:

```bash
mkdir -p backups
docker compose ps

docker compose exec -T postgres sh -c \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' \
  > backups/postgres.dump

cp -p .env backups/environment
docker compose images
```

Verify that the dump is readable without extracting it:

```bash
docker compose exec -T postgres pg_restore --list \
  < backups/postgres.dump
```

Keep the dump, environment copy and recorded image version encrypted and off-host. They can contain application data, password hashes and other secrets. A successful `pg_restore --list` checks the archive structure, not whether a full recovery works.

## Restore test

Use an empty host directory, a separate Compose project and an unused port:

1. Copy this app directory to a disposable location and restore `backups/environment` as `.env`.
2. Set `POSTGRES_PORT=15432` and `POSTGRES_DATA_SOURCE` to an empty absolute directory. Never reuse the production source.
3. Start the isolated database and wait for it to become healthy:

   ```bash
   docker compose -p postgres-restore up -d
   docker compose -p postgres-restore ps
   ```

4. Restore the dump into the freshly initialized database:

   ```bash
   docker compose -p postgres-restore exec -T postgres sh -c \
     'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists' \
     < backups/postgres.dump
   ```

5. Connect through port `15432`, inspect schemas and row counts, and run representative application queries. Restart the container and verify the restored data remains available.
6. Stop the test with `docker compose -p postgres-restore down`. Record the result and securely remove the disposable data when finished.

For a real recovery, restore into an empty source using the recorded compatible major version. Keep the damaged source unchanged until the recovered database passes integrity and application checks. Follow the [official SQL-dump documentation](https://www.postgresql.org/docs/18/backup-dump.html) for parallel dumps, multiple databases, ownership changes and larger recovery designs.
