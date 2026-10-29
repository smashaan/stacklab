# Home Assistant backup and restore

Home Assistant Container supports application-consistent backups through the built-in backup integration. Prefer these to copying a live SQLite database.

## Create a backup

1. Open **Settings > System > Backups** and select **Backup now**.
2. Include Home Assistant settings and, when required, history.
3. Download the completed encrypted archive.
4. Save the backup emergency kit or encryption key separately.
5. Keep an off-host copy and record the image with `docker compose images`.

Local archives are stored below `/config/backups`. A copy left only there does not protect against loss of the host or configuration volume.

## Restore safely

Use a separate disposable Linux host or VM so host networking and port `8123` cannot conflict with production.

1. Install compatible Docker Engine and Compose versions on the test host.
2. Copy this app directory and start a fresh container.
3. During onboarding, choose restore and upload the archive.
4. Supply the encryption key. Allow internet access and adequate free disk space while restoration finishes.
5. Sign in, confirm the expected configuration and helpers, and test representative integrations without unintentionally controlling production devices.
6. Record the result, then remove the disposable deployment.

For a real recovery, restore on the replacement host through onboarding or the backup interface. Preserve the original storage until the restored system passes functional checks. Follow the [official backup documentation](https://www.home-assistant.io/common-tasks/general/backups/) if its current instructions differ from this summary.
