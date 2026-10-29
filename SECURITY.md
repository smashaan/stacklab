# Security Policy

## Supported versions

This repository provides Docker Compose configuration templates rather than a
traditional software release. Security guidance applies to the latest `main`
branch.

## Reporting a vulnerability

If you find a security issue in this repository, please open a private security
advisory or contact the maintainer directly.

Do **not** open a public issue containing:

- Credentials or API keys
- Private IP addresses
- Internal domain names
- Personal information
- Exploit details that could harm other users

## Reporting an upstream vulnerability

If the vulnerability is in a third-party application or container image, report
it to the upstream project first. Add a link to the upstream advisory in an
issue only after it is safe to disclose.

## Secure usage

- Never commit `.env` files, passwords, API keys, or private keys.
- Use `.env.example` only for non-secret placeholders.
- Change default credentials before exposing a service.
- Do not expose databases, admin panels, or internal services to the internet.
- Use a reverse proxy with TLS for services that need remote access.
- Keep Docker, Compose, container images, and the host operating system updated.
- Back up persistent volumes before upgrading containers.
