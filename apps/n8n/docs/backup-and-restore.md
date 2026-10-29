# n8n backup and restore

The SQLite database, n8n state, workflow files and explicit encryption key form one recovery set. Never restore the database without its matching key.

## Back up

From `apps/n8n`, stop the application so SQLite is consistent:

```bash
mkdir -p backups
docker compose stop n8n

docker compose run --rm --no-deps --entrypoint tar n8n \
  -czf - -C /home/node/.n8n . > backups/n8n-data.tar.gz

docker compose run --rm --no-deps --entrypoint tar n8n \
  -czf - -C /files . > backups/n8n-files.tar.gz

cp -p .env backups/environment
docker compose start n8n
docker compose images
```

Encrypt the backup directory and move a copy off the Docker host. It can contain credentials, tokens, personal data and workflow payloads. Record the resolved image version beside it.

## Restore test

Use two empty host directories and a separate Compose project so production volumes remain untouched.

1. Copy this app directory to a disposable location.
2. Extract `n8n-data.tar.gz` and `n8n-files.tar.gz` into separate empty directories.
3. Copy the saved environment file to `.env`, change `N8N_PORT` to an unused port such as `15678`, and set both source variables to the restored absolute directories. Do not change `N8N_ENCRYPTION_KEY`.
4. Ensure UID/GID `1000` can read and write both restored directories.
5. Start and verify the isolated project:

   ```bash
   docker compose -p n8n-restore up -d
   docker compose -p n8n-restore ps
   ```

6. Sign in, open a representative workflow, confirm its credentials decrypt, run it with safe test data and verify required `/files` content.
7. Stop the test with `docker compose -p n8n-restore down`. Keep the recovery report and securely delete the sensitive disposable copy when it is no longer needed.

For real recovery, restore into empty sources and retain the damaged originals until functional checks pass. Use the image version recorded with the backup when current n8n cannot read older state safely.
