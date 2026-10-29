<img src="../../docs/assets/stirling-pdf/stirling-pdf_logo.png" alt="Stirling PDF logo" width="150">

# Stirling PDF

Merge, split, convert and OCR PDFs in your browser. This app runs one upstream Stirling PDF container with persistent settings and documents.

## Supported setup

- Standard stable image (`latest`). Fat, ultra-lite and alpha images are outside this repository's supported configuration.
- Docker-managed named volumes by default. Each persistent source can be changed to an absolute host path through `.env`.
- Authentication enabled and browser access bound to localhost by default.

The stable tag can resolve to a newer release when the image is pulled. The last configuration review was 2026-10-28. See the [upstream image guide](https://docs.stirlingpdf.com/Server/Install/Docker/) for other images and installation methods.

## Before you start

- Install Docker Engine and the Docker Compose plugin (`docker compose`).
- Allow memory for the application plus the host and other services. The default container limit is 4 GB. Large documents can require more.
- Existing users: the previous configuration used `./stirling-data` bind mounts. **Changing to this file does not copy that data into named volumes.** Read the [migration note](docs/backup-and-restore.md#migrating-the-previous-bind-mount-setup) before recreating an existing container.
- Portainer, Dockge and ARM64 have not been tested here.

## Quick start

From the repository root:

```bash
cd apps/stirling-pdf
docker compose up -d
docker compose ps
```

On the Docker host, open <http://localhost:8080>. On a fresh database, sign in with `admin` / `stirling` and change the password immediately. Existing databases keep their users. See [upstream first-login instructions](https://docs.stirlingpdf.com/Server/Security/Sign-in-and-Security/).

For a remote Docker host, first access it through an SSH tunnel from your computer (replace `user@server` with your SSH login):

```bash
ssh -N -L 8080:127.0.0.1:8080 user@server
```

Then open the same localhost address on your computer. The default binds to the Docker host's loopback interface. It is not reachable through the server's LAN address until configured below.

Wait for startup, check `docker compose ps`, then sign in and merge two disposable PDFs. Download and open the result. This functional check matters even if the container reports healthy.

## Configuration

`.env` is optional for Stirling PDF. The defaults work without it and use Docker-managed storage. To customize supported values:

```bash
cp .env.example .env
# Edit .env, then apply:
docker compose up -d
```

| Variable | Default | Purpose |
|---|---|---|
| `STIRLING_PDF_PORT` | `8080` | Browser port on the Docker host |
| `STIRLING_PDF_BIND_ADDRESS` | `127.0.0.1` | Host interface on which the port is published |
| `STIRLING_PDF_LOCALE` | `en-GB` | Default interface language |

After changing the initial password, set `STIRLING_PDF_BIND_ADDRESS` to your server's LAN IP if other LAN devices need access. Open `http://YOUR-SERVER-IP:8080` (or your chosen port). `0.0.0.0` publishes on every IPv4 interface, including public ones. Keep authentication enabled. Use HTTPS for network access carrying sensitive documents. A proxy needs appropriate upload limits and timeouts: [upstream deployment guidance](https://docs.stirlingpdf.com/Server/Production/).

`.env` is for host-specific values only. The supported image, memory limit and authentication remain fixed in `compose.yaml`. Native environment settings override application settings, so a locale selected here also overrides changes made through the interface. See the [configuration reference](https://docs.stirlingpdf.com/Server/Configuration/).

## Your data

| Source variable | Default volume | Container path | What to preserve |
|---|---|---|---|
| `STIRLING_PDF_CONFIGS_SOURCE` | `configs` | `/configs` | Settings, accounts, database and keys. Essential. |
| `STIRLING_PDF_STORAGE_SOURCE` | `storage` | `/storage` | Saved documents. Essential when used. |
| `STIRLING_PDF_CUSTOM_FILES_SOURCE` | `custom-files` | `/customFiles` | Custom assets and signatures when used |
| `STIRLING_PDF_PIPELINE_SOURCE` | `pipeline` | `/pipeline` | Files in processing workflows when used |
| `STIRLING_PDF_TESSDATA_SOURCE` | `tessdata` | `/usr/share/tessdata` | Additional language files. Often reproducible. |
| `STIRLING_PDF_LOGS_SOURCE` | `logs` | `/logs` | Diagnostic history. Optional for recovery. |

Ordinary uploads are processed through the application and do not need host filesystem access. Files saved with server storage remain in the `storage` volume and are accessed through Stirling PDF. Settings, accounts, keys and saved documents stay Docker-managed by default.

To use a host directory, replace the matching volume name in `.env` with an absolute path chosen for that host. Other sources can remain named volumes. Run `docker compose config` and inspect the resolved mounts before applying the change.

> [!WARNING]
> Changing a source does not move existing data. Stirling
> PDF will see an empty location until the old data is copied or restored. Host
> directories may also need different ownership and permissions. Update the
> backup plan before changing a deployment that contains data.

Docker prefixes these names with the Compose project name. Keep that name stable. Runtime data is outside the checkout, but is not encrypted by this configuration or hidden from the host administrator. `docker compose down` retains named volumes. **`docker compose down -v` deletes them**.

## Back up and restore

Follow the [backup and restore guide](docs/backup-and-restore.md). It covers a stopped-container backup and a separate restore deployment, so existing data need not be overwritten.

## Update

Back up first and read the [release notes](https://github.com/Stirling-Tools/Stirling-PDF/releases). The standard stable tag can resolve to a newer image whenever Compose pulls it.

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Repeat the sign-in and PDF-processing check. Record the resolved image before an upgrade if you need a reproducible recovery point. Restoring application files does not guarantee that an older image can read data migrated by a newer release.

## Troubleshooting

| Symptom | Check / action |
|---|---|
| Cannot reach the server from another computer | Default binding is loopback. Use the SSH tunnel or configure the LAN bind address. |
| Port is occupied | Change `STIRLING_PDF_PORT` and recreate the container. |
| Container restarts or stays unhealthy | Read `docker compose logs --tail=100 stirling-pdf`. Check startup errors and memory use. |
| UI language changes do not stick | `STIRLING_PDF_LOCALE` is passed as the native `SYSTEM_DEFAULTLOCALE` setting and takes precedence. |
| Old documents appear missing after this change | Old bind-mounted files were not migrated, or the Compose project name changed. Preserve both stores and follow the migration note. |

For generic commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

Based on the [official Docker example](https://docs.stirlingpdf.com/Server/Install/Docker/). This adaptation follows the standard stable image and uses named volumes by default, loopback access, explicit login, a 4 GB container memory ceiling and an application health endpoint. It does not require a shared network, domain or management UI.

Compared with this repository's older example, storage defaults to named volumes, login is always enabled, and host-specific settings use the variables documented above. The Compose file is now named `compose.yaml` rather than `compose.yml`. Existing bind-mounted data must be migrated before the old deployment is removed.

- [Official website](https://www.stirlingpdf.com/)
- [Application documentation](https://docs.stirlingpdf.com/)
- [Upstream repository](https://github.com/Stirling-Tools/Stirling-PDF)
- [Container image](https://hub.docker.com/r/stirlingtools/stirling-pdf)
- [Release notes](https://github.com/Stirling-Tools/Stirling-PDF/releases)
- [License and licensing details](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/LICENSE)
- [Upstream support and issue reporting](https://github.com/Stirling-Tools/Stirling-PDF/issues)
- [Security policy](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/SECURITY.md)
- [Optional screenshot](../../docs/assets/stirling-pdf/stirling-pdf_dashboard.png)
