# Common tools

These tools are useful for maintaining Docker Compose stacks.

## Docker

- [Docker Engine](https://docs.docker.com/engine/)
- [Docker Compose](https://docs.docker.com/compose/)

Use the repository's [shared troubleshooting guide](troubleshooting.md) for common status, log, validation and lifecycle commands.

## Portainer

[Portainer](https://docs.portainer.io/) provides a web interface for managing Docker environments and can deploy Compose stacks from a Git repository.

## Dockge

[Dockge](https://github.com/louislam/dockge) is a lightweight self-hosted interface for managing Docker Compose stacks.

## Backup tools

Choose a backup method that covers both:

- Docker volumes
- Bind-mounted configuration and media directories

Test restores regularly. A backup that has never been restored is not a proven backup.
