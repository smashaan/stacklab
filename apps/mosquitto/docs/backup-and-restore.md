# Mosquitto backup and restore

Stop the broker before copying its built-in persistence database. Also preserve the generated password file. Git contains only the non-secret broker configuration.

## Back up

From `apps/mosquitto`:

```bash
mkdir -p backups
docker compose stop mosquitto

docker compose run --rm --no-deps --entrypoint tar mosquitto \
  -czf - -C /mosquitto/data . > backups/mosquitto-data.tar.gz

cp -p config/passwords backups/passwords
docker compose start mosquitto
```

Store the archive and password file together in encrypted, access-controlled off-host storage. Record the resolved image shown by `docker compose images` and test the backup before relying on it.

## Restore test

Use a disposable directory and a different host port so production data is not overwritten.

1. Copy this app directory to the disposable location.
2. Copy the backed-up `passwords` file into its `config` directory.
3. Set `MOSQUITTO_PORT=11883` and `MOSQUITTO_DATA_SOURCE` to an empty absolute directory in its `.env`.
4. Extract `mosquitto-data.tar.gz` into that data directory and ensure UID/GID `1883` can read and write it.
5. Start the disposable deployment with a distinct project name:

   ```bash
   docker compose -p mosquitto-restore up -d
   ```

6. Run the authenticated publish/subscribe check against port `11883`, then verify a representative retained message or durable session.
7. Stop the test with `docker compose -p mosquitto-restore down`. Remove its disposable files only after recording the result.

For real recovery, keep the damaged storage unchanged, restore into an empty source, start the broker and validate clients before retiring the old data.
