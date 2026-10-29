# Extensions

Add this directory only when the stack has a maintained optional addition. Every
service required to deliver the stack's stated goal belongs in `compose.yaml`.

Document for each extension:

- What optional capability it adds
- Any setup required before enabling it
- The complete `docker compose -f` command used to enable it
- Dependencies or conflicts with other extensions
- How to disable it cleanly
- How the combined configuration was validated

Remove this directory when the stack has no extensions.

The included `compose.shared-network.yaml` is a scaffold. Attach only the
service that another project needs to reach. Remove the file when cross-project
communication is unnecessary.
