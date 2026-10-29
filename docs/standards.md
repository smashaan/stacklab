# Deployment standard

Provide one understandable Compose deployment with enough instructions to start it, keep its data, update it and recover it.

## Scope and layout

Docker Compose on one host is the supported deployment format.

Classify a deployment by the main reason a user installs it. An app provides one primary product. Its Compose file can include services required for every supported installation, such as a dedicated database or cache.

A stack connects two or more independently useful products for a shared goal.
Each product has a meaningful role in the combined solution rather than only supporting one primary product.

Keep the base Compose file useful by itself. Do not fill it with commented services or profiles. Put optional services, devices and networking in named Compose files under `extensions/`. Users select only the extensions they need.

Keep independently useful products as separate apps. For example, PostgreSQL and Adminer each have their own app. Their shared-network extensions let users connect them without duplicating either deployment.

Plugins and integrations installed inside an application are application features. Link to upstream instructions instead of copying a changing list into Compose. A feature that runs as another container is a separate app. Use extensions and shared networking to connect it when needed.

Use upstream container images and support one recommended stable image channel per deployment. Link to upstream guides for other image variants, native binaries, Kubernetes and Swarm. This repository does not publish replacement images for upstream applications.

Use `apps/` for standalone products and `stacks/` for grouped solutions. Existing examples are being brought into this standard gradually.

```text
README.md                   # Purpose, catalog link and getting started
CONTRIBUTING.md             # How to submit and verify a change
apps/<name>/
  compose.yaml              # Required: one recommended app deployment
  README.md                 # Required: setup and operation
  .env.example              # Only if configuration is exposed
  extensions/               # Optional Compose additions and their instructions
    compose.<feature>.yaml  # One service, device or network addition
  config/                   # Only if tracked application config is required
  docs/                     # Only for longer app-specific guides
stacks/<name>/
  compose.yaml              # Required: one recommended deployment
  README.md                 # Required: setup and operation
  .env.example              # Only if configuration is exposed
  extensions/               # Optional additions that preserve the stack goal
  config/                   # Only if tracked application config is required
  docs/                     # Only for longer application-specific guides
templates/app/              # The app contributor scaffold
templates/stack/            # The grouped stack contributor scaffold
docs/                       # Shared standards and Compose guidance
  README.md                 # Documentation index
  catalog.md                # Available deployments and their purpose
  wishlist.md               # Future ideas, not supported deployments
  assets/<application>/     # Optional, small documentation images
```

No empty optional folders, category nesting, metadata schema or generator is required. Copyable configuration and a short README are the starting point.

## Extensions

An extension adds one optional capability without changing the purpose of the base deployment. Examples include an administration interface, a device mapping or access to a shared network. Each extension must have a narrow purpose and work when merged with the base file.

Apps and stacks can both have extensions. An app extension must not replace the primary product. A stack extension must not contain a product required for the stack to achieve its stated goal. Put every required stack service directly in the stack's base `compose.yaml`.

Select extensions with explicit, ordered `-f` arguments. Keep extension selection out of `.env`, which is reserved for deployment values. Document the complete command and use the same files for `config`, `up`, `pull`, `logs` and `down`. Before removing an extension, run `down` with the extension included so Compose can remove its containers.
Do not commit an automatically loaded `compose.override.yaml`, because it prevents the base deployment from remaining predictable.

An optional external network can connect apps managed as separate Compose projects. The base app stays on its private project network. Attach only the service that needs cross-app communication to the shared network. Applications using host networking cannot also join a Compose bridge network and must be reached through the Docker host address.

See [Compose extensions and shared networking](extensions.md) for the user workflow and naming rules.

## Configuration contract

Use the configuration mechanism that matches the kind of change:

| Change | Mechanism | Examples |
|---|---|---|
| Value inside the maintained deployment | `.env` | Port, bind address, locale, required secret, persistent mount source |
| Maintained optional capability | Named file under `extensions/` | Shared network, optional companion service, device support |
| User-specific structural change | Untracked `compose.override.yaml` | Add labels, replace commands, change an undocumented mount |

Persistent mounts use `<PREFIX>_<PURPOSE>_SOURCE` variables when users may need to choose between Docker-managed storage and a host path. The default value must be a declared named volume. Do not expose other structural Compose fields as variables only to make every customization use `.env`.

- Use `compose.yaml` and modern `docker compose` commands.
- A new user follows one recommended deployment. *Optional settings have working defaults. `.env` is mandatory only when required input such as a secret exists.*
- Every README must say whether `.env` is required or optional before its quick start commands. Required variables have no working default. Optional variables must resolve to a usable and safe deployment when `.env` is absent.
- Prefix host-specific deployment controls with the application name, such as `<PREFIX>_PORT`, `<PREFIX>_BIND_ADDRESS` and `<PREFIX>_LOCALE`. Expose only values users commonly need to change between hosts.
- Use the application's native variable names inside `environment`.
  **Do not create aliases for every upstream option or forward the entire host `.env`**.
- Keep Compose defaults, `.env.example` and the README consistent. A variable in `.env` reaches an application only when Compose passes it explicitly.
- Follow the upstream stable image channel when it is documented and maintained.
  Pin an image only when upstream has no reliable stable channel or an automatic upgrade would be unsafe. Record the resolved image for backup and recovery.
- Support one image variant. Link to upstream documentation for alternatives.
- A memory limit is a ceiling, not a reservation or a measured requirement.
- Required secrets have no usable default. Use `${VARIABLE:?Set VARIABLE}`.
- Use the default project network. No fixed container names or global network dependencies unless the application requires them.
- Bind ordinary web interfaces to loopback initially. Explain remote access and how to enable LAN access. Document exceptions for network/hardware services.
- Keep authentication enabled when supported. Explain initial account setup.
- Add health checks using commands actually present in the image. Document any required host networking, elevated permissions or device access.

Use an extension only when an optional service or structural change cannot be expressed with an ordinary variable. Avoid duplicate full Compose files for changes that a variable can express.

## Storage

Use project-scoped named volumes for application-managed data. They keep mutable data outside Git and avoid requiring a host directory layout. They do not provide encryption or protection from the Docker/host administrator, and are not backups.

When storage location is configurable, use a source variable with a named-volume default:

```yaml
services:
  app:
    volumes:
      - "${APP_DATA_SOURCE:-app-data}:/data"

volumes:
  app-data:
```

The source can be the default volume name or an absolute host path. Declare the default volume at the end of the Compose file even when a user can replace it.
An unused declaration is valid and does not attach the volume to the container.

List every supported source variable in `.env.example`. Explain that changing a source does not copy existing data, can change file permissions, and changes what must be backed up. Recommend `docker compose config` before applying a storage change. Do not change storage sources casually on a deployment that contains data.

Document storage sources in two places. Keep `.env.example` comments short and close to the variables because users edit that file directly. Put the complete explanation in the README, including defaults, permissions, migration, backup, restore and how to inspect the resolved mounts. Do not repeat the full warning beside every variable.

Start every environment example with an `Instructions` heading between comment separators. Explain whether the user must copy the file and remind them not to commit `.env`. Follow it with `Required settings` and `Optional settings` using the same format. Put required values first and omit any empty settings section. Use short comments beside variables instead of creating more categories.

Keep required values active with an obvious replacement value such as `CHANGE_ME`. Keep optional values with working Compose defaults commented out in `.env.example`. Show the effective default on the commented line so users can uncomment and edit only the settings they want to change.

```env
# -----------------------------------------------------------------------------
# Instructions
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Required settings
# -----------------------------------------------------------------------------
```

Bind mounts are appropriate for user-managed media, imports or editable files.
Mutable bind-mounted data must use an absolute path outside the checkout.
Read-only tracked configuration such as `./config/app.conf` is allowed.
Do not force a named volume on an application whose core workflow needs host files.

Changing between bind mounts and named volumes does not migrate data. Changing project names can select different volumes. Explain migration before altering storage.

## Documentation

Every README includes a useful description, prerequisites, a quick start, a first login or functional check, configuration when present, persistence, updates and upstream references.
Stateful applications include backup and restore guidance. Stateless applications explicitly say there is no application data to back up.

End each deployment guide with `About this setup`. Briefly explain which upstream example or guidance the Compose configuration follows and any meaningful changes made by this repository. Link to the official documentation, source repository, container image, release notes, license, upstream support and security policy when those resources exist. Stacks provide a short subsection with these links for every main product. Distinguish upstream product problems from issues in this repository's Compose files. Link to the upstream license instead of copying its text into the deployment guide.

Templates use HTML comments for contributor instructions because those comments do not appear in the rendered README. Published deployment guides must remove those comments. Use Markdown notes and warnings only for information users need while deploying or operating the application.

Write each ordinary paragraph as continuous prose. Do not insert manual line breaks inside a sentence or paragraph. Keep deliberate line breaks for lists, tables, code blocks, alerts and other Markdown structures.

Keep short application-specific troubleshooting in the README. Put longer recovery or deployment tutorials in the deployment's `docs/` directory. Shared Docker commands belong in root `docs/`. General product tutorials belong upstream. Remove empty sections and template instructions from published deployments.

Logos are optional. When included, place the logo above the page title and use a short, specific `alt` value such as `Adminer logo`. Keep `alt` on every image for accessibility and for readers when an image cannot load. Prefer an official asset and record its source and license when attribution is required.

Screenshots are optional. Prefer one optimized image where it helps. Aim for roughly 200 KB, with exceptions for legibility. Keep large galleries/videos external, link to upstream demos, sanitize screenshots and record attribution.
Use existing `docs/assets/<app>/` paths to avoid unnecessary asset moves.

## Testing and support claims

Run `docker compose config --quiet` with defaults and the example environment.
Review resolved ports, volumes, environment and resource limits. Parsing alone does not establish a working application.

Before describing a deployment as runtime-tested, follow the quick start, log in, perform a representative action, recreate it to check persistence, and verify its restore procedure in an isolated deployment. Record the tested image and platform. Do not describe Portainer, Dockge or ARM64 as tested without evidence.
Configuration-only examples can be shared before runtime testing when the limitation is clear in the pull request or commit message.

## References

- [Docker volumes](https://docs.docker.com/engine/storage/volumes/)
- [Compose interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)
- [Compose overrides](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)
