# Traefik certificate-state backup and restore

The base Traefik deployment has no persistent runtime data. This guide applies only to `extensions/compose.letsencrypt.yaml` and its `/letsencrypt` storage.

ACME state contains account credentials, certificate private keys and issued certificates. Encrypt backups, restrict access and keep an off-host copy. The state is renewable, but preserving it avoids unnecessary account creation and certificate issuance against rate limits.

## Back up

Stop Traefik briefly so the ACME file cannot change during the archive:

```bash
mkdir -p backups
docker compose -f compose.yaml \
  -f extensions/compose.letsencrypt.yaml stop traefik

docker run --rm \
  -v traefik_certificates:/source:ro \
  -v "$PWD/backups:/backup" \
  alpine:3.22 tar -czf /backup/traefik-certificates.tar.gz -C /source .

cp -p .env backups/environment

docker compose -f compose.yaml \
  -f extensions/compose.letsencrypt.yaml start traefik

docker compose -f compose.yaml \
  -f extensions/compose.letsencrypt.yaml images
```

The `traefik_certificates` name assumes the default Compose project and named-volume source. Confirm the actual source with the full `docker compose ... config` command. If `TRAEFIK_CERTIFICATES_SOURCE` is an absolute host path or the project name differs, archive that resolved source instead.

Verify that the archive is non-empty and keep it together with the environment copy and image-version record. Do not print `acme.json` or commit it to Git.

## Restore test

Use a disposable host or isolated Docker environment. A test connected to production DNS can renew or replace live certificates, so prevent public traffic and certificate issuance while inspecting the restored state.

1. Copy this app directory and restore `backups/environment` as `.env`.
2. Create an empty certificate volume and extract the archive:

   ```bash
   docker volume create traefik-restore-certificates

   docker run --rm \
     -v traefik-restore-certificates:/target \
     -v "$PWD/backups:/backup:ro" \
     alpine:3.22 tar -xzf /backup/traefik-certificates.tar.gz -C /target
   ```

3. Set `TRAEFIK_CERTIFICATES_SOURCE=traefik-restore-certificates`. Inspect `docker compose config` and confirm `/letsencrypt` resolves to that volume.
4. With outbound ACME access blocked or the resolver temporarily omitted in an untracked test override, start Traefik and inspect logs for successful state loading.
5. Confirm the archive contains the expected `acme.json` with file mode `600` without displaying its contents.
6. Stop the test, record the result and remove the disposable sensitive copy when finished.

For real recovery, restore into an empty source before starting Traefik with the Let's Encrypt extension. Confirm DNS and router configuration, then allow ACME traffic and verify certificate expiry dates. Preserve failed originals until routed applications pass checks.
