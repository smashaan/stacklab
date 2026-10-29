# Extensions

Add this directory only when the app has a maintained optional Compose addition.
Name each file `compose.<feature>.yaml` and give it one clear purpose.

Document for each extension:

- What it adds or changes
- Any setup required before enabling it
- The complete `docker compose -f` command used to enable it
- Dependencies or conflicts with other extensions
- How the combined configuration was validated

Remove this directory when the app has no extensions.

The included `compose.shared-network.yaml` is a scaffold. Rename the `app`
service when the base Compose file uses another service name. Remove the file
when cross-project communication is unnecessary.
