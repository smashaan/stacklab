# Compose extensions and shared networking

This repository uses three configuration layers. `.env` changes supported values inside the maintained deployment, including persistent mount sources. Files under `extensions/` enable maintained optional capabilities. An untracked `compose.override.yaml` belongs to the user and handles changes that the published configuration does not support.

Each app starts from its base `compose.yaml`. Files under `extensions/` add one optional service or structural change without modifying that base file.

An extension preserves the app's primary purpose. If a service is required for that purpose, put it directly in the base Compose file.

## Select extensions

Select an extension explicitly with `-f`. Keep extension selection out of `.env` so that file contains only deployment values:

```bash
docker compose -f compose.yaml \
  -f extensions/compose.shared-network.yaml up -d
```

Use the same ordered `-f` arguments for every lifecycle command, including `config`, `pull`, `logs` and `down`. To disable an extension, first run `down` with the extension included. Then start the base deployment without its `-f` argument. Otherwise Compose may not see extension containers during cleanup.

To select several extensions, add each file in merge order:

```bash
docker compose -f compose.yaml \
  -f extensions/compose.first.yaml \
  -f extensions/compose.second.yaml up -d
```

Validate the merged configuration before starting it:

```bash
docker compose -f compose.yaml \
  -f extensions/compose.shared-network.yaml config --quiet
```

All relative paths in merged files are resolved from the directory containing the base Compose file. Each app README must document dependencies and conflicts between extensions.

## Connect separate apps

Apps use private project networks by default. Create the optional shared network once when two app projects need direct container communication:

```bash
docker network create stacklab
```

Enable `compose.shared-network.yaml` for each participating app. Containers can then use Compose service names such as `postgres` instead of fixed IP addresses.
Keep databases, caches and other internal services off the shared network unless another trusted app needs them.

An app using `network_mode: host`, such as the current Home Assistant setup, cannot also join this bridge network. Other containers must reach it through the Docker host address.

## Other local changes

Published deployments can expose supported storage sources through `.env`. For other structural changes, users can create `compose.override.yaml` inside the deployment directory. This file is ignored by Git and loaded automatically by Compose.

For example, this local file replaces an undocumented mount:

```yaml
services:
  app:
    volumes:
      - /CHANGE_THIS/imports:/imports
```

Replace `CHANGE_THIS` before using the file. It is a placeholder and not a recommended host directory.

Compose merges volume entries by their container target, so `/imports` replaces the base mount at `/imports`. Other mounts remain unchanged. Run `docker compose config` and inspect the resolved mounts before starting.

The user owns migration, permissions, backup and recovery for local overrides.
Use the documented `.env` source variables for supported persistent mounts.

## Maintainer rules

- Keep `compose.yaml` runnable without extensions.
- Keep every service required for the app's supported purpose in its base Compose file.
- Give each extension one clear purpose.
- Use `compose.<feature>.yaml` names.
- Do not use extensions for ordinary port, locale or bind-address changes.
- Document extension dependencies and incompatible combinations.
- Validate the base configuration and every documented combination.
- Document how to disable the extension cleanly.
- Do not commit `compose.override.yaml`, because it is reserved for local user customization and Compose loads it automatically.

References:

- [Merge Compose files](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)
- [Connect multiple Compose projects](https://docs.docker.com/compose/how-tos/networking/)
