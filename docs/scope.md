# Project scope

Stacklab maintains curated Docker Compose deployments for home servers and small teams. Its focus is safe defaults, clear data ownership, practical updates and recoverable operation on one Docker host.

## Repository model

Every supported product lives under `apps/<name>/`. Its directory contains the Compose file and the guidance needed to run it. It can also contain tracked configuration, optional extensions, recovery guides and useful diagrams or screenshots.

A product can include a dedicated database, cache or other supporting service when that service exists only to make the primary product work. Independently useful products remain separate apps and can connect through maintained extensions when needed.

## Boundaries

Stacklab does not maintain custom application products, replacement container images, native installers, Kubernetes deployments or graphical app-store packages. It does not group products merely to start several containers with one command.

Multi-product solutions belong here only when Stacklab maintains an integration that separate deployments cannot provide. Useful integrations could include configured data sources, shared credentials, tested workflows and coordinated recovery.

## Optional management tooling

Every deployment must remain usable with ordinary Docker Compose commands. Any management tool must stay optional and show what it changes.

A future command-line tool could list deployments, check host requirements, validate resolved configuration, report data locations and prepare update plans. It should show important commands, avoid storing secrets and never hide destructive actions.

A custom graphical interface is outside the current scope. It would need Docker socket access, authentication, secret handling, persistent state and its own update process. Portainer and Dockge already provide general graphical management.
