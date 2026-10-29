<!-- TODO: Replace this title with the application name. -->
# Application name

<!-- TEMPLATE ANATOMY
This README is for one primary product. Its Compose file can include a dedicated
database, cache or other service required for every supported installation.
Optional services and structural changes belong in named files under
`extensions/`. Independently useful products remain separate apps and can use
shared-network extensions to communicate.

Keep every section that applies and remove every instruction comment before
publishing. Write for a person using Docker Compose for the first time. Explain
the reason behind unusual commands or settings, but link upstream instead of
copying full product manuals.
-->

<!-- TODO: In one or two sentences, explain what the application does and why
someone would run it. Mention bundled helper services only when users interact
with them. -->

## Supported setup

<!-- State the exact scope maintained by this repository. This lets readers see
what is supported without reading the entire guide. -->

<!-- TODO: Replace each explanation below with the maintained setup. Remove a
line when it does not apply. -->

- Image channel: State the upstream stable channel and image variant
- Storage: State whether data uses named volumes or required host paths
- Network access: State the default host binding and exposed interfaces
- Required services: List a dedicated database or cache when included
- Validation: Record completed checks, platform, Compose version and test date

<!-- TODO: Link to upstream documentation for other image variants and
deployment methods. -->

## Before you start

<!-- List Docker requirements, minimum resources, supported architecture,
required devices and external dependencies. Separate upstream requirements from
what maintainers measured. Do not repeat generic Docker installation steps. -->

- Docker Engine and the Docker Compose plugin (`docker compose`)
- Application-specific requirement

## Quick start

<!-- State clearly whether .env is required or optional. When required values
exist, copy and edit it before starting. When every variable has a working
default, say that .env is optional and leave the copy step for Configuration. -->

<!-- TODO: Say whether `.env` is required or optional and explain why. -->

From the repository root:

```bash
cd apps/application-name
docker compose up -d
docker compose ps
```

Open <http://localhost:8080> on the Docker host.

<!-- TODO: Explain the first login, initial account creation and one useful
success check. Explain remote access when the service binds to loopback. -->

## Configuration

<!-- Include this section only when .env.example exists. Begin with either
".env is required" and explain why, or ".env is optional" and say the defaults
work without it. Document only variables that Compose reads. -->

<!-- TODO: Repeat whether `.env` is required or optional. Explain what happens
when it is absent. -->

```bash
cp .env.example .env
# Edit .env, then apply the changes.
docker compose up -d
```

| Variable | Default | Purpose |
|---|---|---|
| `APP_PORT` | `8080` | Browser port on the Docker host |
| `APP_BIND_ADDRESS` | `127.0.0.1` | Host interfaces that accept connections |
| `APP_DATA_SOURCE` | `app-data` | Named volume or absolute host path for persistent data |

> [!WARNING]
> Change a storage source only after locating and backing up the current data.
> A new source starts empty because Compose does not move data.
> Host paths can also change permissions and backup requirements. Run
> `docker compose config` and inspect the resolved mounts before applying it.

<!-- Keep only the short editing instructions in .env.example. Keep this fuller
warning in the README so users can understand migration, permissions, backup and
restore before changing a source. -->

## Extensions

<!-- Include this section only when extensions/ contains maintained files. State
what each extension changes, its prerequisites and the complete `docker compose
-f` command that enables it. Link to ../../docs/extensions.md for the shared
workflow. -->

| Extension | Purpose | Prerequisite |
|---|---|---|
| `compose.feature-name.yaml` | Describe the optional capability | State required setup or `None` |

## Your data

<!-- List every persistent volume and bind mount. Say what it contains, whether
it must be backed up and whether the application can recreate it. -->

| Volume or path | Contents | Backup need |
|---|---|---|
| `APP_DATA_SOURCE` mounted at `/data` | Describe the persistent data | State whether a backup is required |

Named volumes keep runtime data outside the checkout. They do not encrypt it. `docker compose down` keeps them. `docker compose down -v` deletes them.

## Back up and restore

<!-- Give commands that produce a consistent backup and a separate restore
procedure. State when writes must stop and where backups should be kept. Link to
docs/backup-and-restore.md when the procedure is too long. Say explicitly when
the app has no persistent data. -->

<!-- TODO: Add backup and restore commands, then include a check that proves the
restored application works. -->

## Update

<!-- Explain release notes, backup requirements, migrations and how to confirm
the app still works. Mention special rules for major version upgrades. -->

```bash
docker compose pull
docker compose up -d
docker compose ps
```

## Troubleshooting

<!-- Include only known application-specific symptoms and useful diagnostic
steps. Link to ../../docs/troubleshooting.md for general Compose commands. Remove
this section when there are no app-specific findings. -->

### Visible symptom

<!-- TODO: Describe the likely cause, useful diagnostic commands and safe fix. -->

## About this setup

<!-- Explain briefly which upstream example this deployment follows and any
meaningful changes made by this repository. Keep only links that exist. Use the
upstream support link for product problems. Repository-specific Compose problems
belong in this repository's issue tracker. -->

- [Official website](https://example.com)
- [Documentation](https://example.com/docs)
- [Source repository](https://example.com/source)
- [Container image](https://example.com/image)
- [Release notes](https://example.com/releases)
- [License](https://example.com/license)
- [Upstream support](https://example.com/support)
- [Security policy](https://example.com/security)

<!-- Add config/ only for tracked runtime configuration. Keep the normal setup,
operation and a short troubleshooting table in this README. Add docs/ only for
substantial procedures such as backup and restore, migration, recovery or
advanced troubleshooting. Add assets/ only for deployment-specific screenshots
or diagrams that explain a concrete instruction. Repository-wide media belongs
in ../../docs/assets/common/. Do not create empty directories. -->
