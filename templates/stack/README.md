<!-- TODO: Replace this title with the stack name. -->
# Stack name

<!-- TEMPLATE ANATOMY
Use this template when two or more independently useful products work together for a
shared goal. If one product is the reason for installation and every other
service only supports it, use templates/app instead.

Keep sections that apply and remove every instruction comment before publishing.
Describe the combined workflow and the connections between products. Link to
each product's documentation for features outside this integration.
-->

<!-- TODO: In one or two sentences, explain the shared goal and the result a
person gets by running the products together. -->

## What is included

<!-- List every independent product and its role. Supporting databases and caches
can appear here when knowing about them helps operation. -->

| Product | Role in this stack | User access |
|---|---|---|
| Product one | Explain its role | State its URL, port or `Internal only` |
| Product two | Explain its role | State its URL, port or `Internal only` |

## How it works

<!-- Explain the path between products in a short paragraph. Include a small
diagram only when it makes the data flow or network boundaries easier to see. -->

<!-- TODO: Describe what starts the workflow, what moves between products and
the final result. -->

## Supported setup

<!-- TODO: Replace each explanation with details for this stack. -->

- Image channels: State one maintained stable channel for each product
- Storage: State the named volumes and required host paths
- Network access: State default bindings and services that remain internal
- Validation: Record configuration, runtime, workflow and recovery checks

## Before you start

<!-- List shared resource needs, required accounts, devices, host paths and
external systems. Say which products require initial setup before integration. -->

- Docker Engine and the Docker Compose plugin (`docker compose`)
- Stack-specific requirement

## Quick start

<!-- Give one complete order. State whether .env is required or optional. Include
the copy and edit steps before starting only when required values exist. -->

<!-- TODO: Say whether `.env` is required or optional and explain why. -->

From the repository root:

```bash
cd stacks/stack-name
# Add `cp .env.example .env` here only when .env is required.
docker compose up -d
docker compose ps
```

<!-- TODO: Explain the first-time setup order and give one check that proves the
complete workflow works. -->

## Configuration

<!-- Begin with either ".env is required" and explain why, or ".env is optional"
and say the defaults work without it. Group variables by product when that helps.
Document only values read by Compose. -->

<!-- TODO: Repeat whether `.env` is required or optional and explain what
happens when it is absent. -->

| Variable | Default | Used by | Purpose |
|---|---|---|---|
| `STACK_BIND_ADDRESS` | `127.0.0.1` | Product one | Host interfaces that accept connections |
| `PRODUCT_ONE_PORT` | `8080` | Product one | Browser port on the Docker host |
| `PRODUCT_ONE_DATA_SOURCE` | `product-one-data` | Product one | Named volume or absolute host path |
| `PRODUCT_TWO_DATA_SOURCE` | `product-two-data` | Product two | Named volume or absolute host path |

> [!WARNING]
> Changing a storage source does not move existing data. A new source starts
> empty and may use different file permissions. Review the resolved mounts
> with `docker compose config` and update the backup plan before applying it.

<!-- Keep only the short editing instructions in .env.example. Keep this fuller
warning in the README so users can understand migration, permissions, backup and
restore before changing a source. -->

## Extensions

<!-- Include this section only when extensions/ contains maintained files. A
stack extension may add an optional interface, device, network or integration.
Every service required for the stack's stated goal belongs in compose.yaml.
State prerequisites, the complete `docker compose -f` command and how to disable
each extension. Link to ../../docs/extensions.md for the shared workflow. -->

| Extension | Purpose | Prerequisite |
|---|---|---|
| `compose.feature-name.yaml` | Describe the optional capability | State required setup or `None` |

## Access and connections

<!-- State the URL for each user-facing product and the Compose service names
used for internal connections. Explain authentication and safe LAN access. -->

| Product | Address | Login or connection notes |
|---|---|---|
| Product one | `http://localhost:8080` | Explain initial account setup |

## Your data

<!-- Show which product owns each volume or path. Explain dependencies between
data sets and whether restoring one product requires a matching backup from
another. -->

| Owner | Volume or path | Contents | Backup need |
|---|---|---|---|
| Product one | `product-one-data` | Describe the persistent data | State whether a backup is required |

## Back up and restore

<!-- Give a consistent backup order and restore order. State whether the whole
stack must stop. Include a full workflow check after restoration. Use a longer
guide in docs/ when necessary. -->

<!-- TODO: Add the backup, restore and verification procedure. -->

## Update

<!-- Explain compatibility checks and the safe product update order. Mention
migrations or coordinated versions where needed. -->

```bash
docker compose pull
docker compose up -d
docker compose ps
```

## Troubleshooting

<!-- Focus on failures at the boundaries between products. Link to each upstream
project for product-specific problems and ../../docs/troubleshooting.md for
general Compose commands. -->

### Integration symptom

<!-- TODO: Explain how to locate the failing connection and restore the
workflow. -->

## About this setup

<!-- Explain briefly where the integration design came from and any meaningful
changes made by this repository. Provide the same links for each main product.
Use upstream support for product problems and this repository's issue tracker
for problems in the supplied Compose configuration. Omit links that do not
exist. -->

### Product one

- [Official website](https://example.com)
- [Documentation](https://example.com/docs)
- [Source repository](https://example.com/source)
- [Container image](https://example.com/image)
- [Release notes](https://example.com/releases)
- [License](https://example.com/license)
- [Upstream support](https://example.com/support)
- [Security policy](https://example.com/security)

### Product two

- [Official website](https://example.com)
- [Documentation](https://example.com/docs)
- [Source repository](https://example.com/source)
- [Container image](https://example.com/image)
- [Release notes](https://example.com/releases)
- [License](https://example.com/license)
- [Upstream support](https://example.com/support)
- [Security policy](https://example.com/security)
