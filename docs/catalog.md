# Deployment catalog

This catalog is the repository's inventory of supported product deployments. A listed deployment is not automatically suitable for every production environment.

## Apps

| App | Purpose |
| --- | --- |
| [Adminer](../apps/adminer/README.md) | Manage databases in a browser |
| [Appsmith](../apps/appsmith/README.md) | Build internal tools |
| [Home Assistant](../apps/home-assistant/README.md) | Run home automation |
| [LaTeX](../apps/latex/README.md) | Compile LaTeX documents |
| [Mosquitto](../apps/mosquitto/README.md) | Provide MQTT messaging |
| [n8n](../apps/n8n/README.md) | Automate workflows |
| [Nextcloud](../apps/nextcloud/README.md) | Host files and collaboration tools |
| [nginx](../apps/nginx/README.md) | Serve static sites and proxy HTTP traffic |
| [Node-RED](../apps/node-red/README.md) | Build event-driven automations |
| [Portainer](../apps/portainer/README.md) | Manage container environments |
| [PostgreSQL](../apps/postgres/README.md) | Run a relational database |
| [SFTPGo](../apps/sftpgo/README.md) | Share files through SFTP and a browser |
| [Stirling PDF](../apps/stirling-pdf/README.md) | Work with PDF documents in a browser |
| [Traefik](../apps/traefik/README.md) | Route traffic to services |

Nextcloud remains an app even though its deployment includes a required database. PostgreSQL and Adminer are separate apps that can communicate through their shared-network extensions.
