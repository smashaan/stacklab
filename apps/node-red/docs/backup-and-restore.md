# Node-RED backup and restore

The `/data` directory and `NODE_RED_CREDENTIAL_SECRET` form one recovery set. Without the matching secret, encrypted node credentials cannot be restored.

## Back up

Stop Node-RED so flows, installed-node metadata and context stores are consistent:

```bash
mkdir -p backups
docker compose stop node-red

docker compose run --rm --no-deps --entrypoint tar node-red \
  -czf - -C /data . > backups/node-red-data.tar.gz

cp -p .env backups/environment
docker compose start node-red
docker compose images
```

Encrypt the backup directory, restrict access and keep an off-host copy. It can contain credentials, tokens, workflow payloads and project repository data.

## Restore test

Use an empty host directory and separate Compose project:

1. Copy this app directory to a disposable location.
2. Extract `node-red-data.tar.gz` into an empty directory and make it writable by UID/GID `1000`.
3. Restore `environment` as `.env`, set `NODE_RED_PORT=11880` and point `NODE_RED_DATA_SOURCE` to the restored absolute directory. Do not change `NODE_RED_CREDENTIAL_SECRET`.
4. Start the isolated project:

   ```bash
   docker compose -p node-red-restore up -d
   docker compose -p node-red-restore ps
   ```

5. Sign in through port `11880`, inspect the expected flows and projects, deploy a safe representative flow and verify credential-dependent nodes can still initialize.
6. Stop with `docker compose -p node-red-restore down`. Record the result and securely remove the disposable sensitive copy when finished.

For a real recovery, restore into an empty source and preserve damaged originals until functional checks pass. Use the image version recorded with the backup if a current runtime or contributed node is incompatible.
