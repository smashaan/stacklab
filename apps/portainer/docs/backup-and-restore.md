# Portainer backup and restore

Portainer's built-in backup archives everything it stores in `/data`, including its database, access controls, certificates, environment metadata, credentials and Portainer-managed stack definitions. Treat the archive and its password as sensitive administrative material.

It does **not** contain the managed Docker host's containers, images, volumes or application data. Those require independent backups.

## Back up

1. Sign in to Portainer as an administrator.
2. Open **Settings** and find **Back up Portainer**.
3. Leave **Download backup file** selected.
4. Enable password protection and use a unique password stored separately in a password manager.
5. Select **Download backup** and retain the resulting `.tar.gz` file.
6. Record the running image version:

   ```bash
   docker compose images
   ```

Store the archive encrypted, off the Docker host and together with the image-version record. Confirm that the downloaded file is non-empty. Avoid unpacking it because its contents are sensitive.

## Restore test

Portainer only offers configuration restore during initialization of a fresh instance with empty `/data`. Because this deployment controls its attached Docker daemon, perform the test on a disposable Linux VM or another isolated Docker host. Do not run it as a second project connected to the production socket.

1. Copy this app directory and the backup archive to the disposable host.
2. Set an unused HTTPS port if necessary and start Portainer with an empty data source:

   ```bash
   docker compose up -d
   docker compose logs portainer
   ```

3. Open the HTTPS URL and complete the setup-token prompt within five minutes.
4. Expand **Restore Portainer from backup**, select the `.tar.gz` file, enter its password and start the restore.
5. Sign in with the restored credentials and verify users, settings and environment metadata. Expect the original environment to be unavailable unless its connection endpoint is reachable from the isolated host.
6. Record the result and destroy the disposable host or securely remove its restored data when finished.

For a real recovery, deploy the image version recorded with the backup against an empty data source, restore through the same initialization workflow, and upgrade only after recovery checks pass. Preserve the failed source unchanged until the restored instance is accepted.

Follow the [official backup and restore procedure](https://docs.portainer.io/admin/settings/general) if the interface or supported workflow changes.
