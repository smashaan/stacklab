# Contributing

Help make each application easy to start, understand and maintain. Improvements
to existing setups, recovery instructions and test evidence are as useful as new
applications.

## Add or improve a deployment

1. Check `apps/` and open issues for duplicates.
2. Read the [deployment standard](docs/standards.md).
3. Copy the app template for one primary product and any services required for
   that product to run.

   ```bash
   cp -r templates/app apps/<app-name>
   ```

4. Replace every placeholder and remove unused settings. Use lowercase,
   hyphenated directory names. Prefer an upstream image and record the source
   configuration. Put optional services and structural changes in named files
   under `extensions/`. Add that directory only when it contains a maintained
   extension.
5. Write the README for someone deploying this application for the first time.
   Include data, updates and recovery. Keep detailed tutorials in the deployment's
   `docs/` directory when needed.
   Keep template directions inside HTML comments so they do not appear in the
   rendered README. Use GitHub Markdown alerts only for information the person
   deploying the app needs to see. Remove every template comment before publishing.
   Keep ordinary paragraphs continuous instead of manually breaking their lines. Preserve line breaks that belong to lists, tables, code blocks and alerts.
   When storage sources are configurable, add short instructions beside them in
   `.env.example` and explain the full consequences once in the README. State
   that the default is a Docker-managed volume, an enabled value must be an
   absolute host path, and changing it does not move existing data. Cover host
   permissions, backups and `docker compose config` in the README.
   Start every environment example with the standard `Instructions` heading
   between comment separators. Use the same format for `Required settings` and
   `Optional settings`. Put required values first and omit any empty settings
   section. Use short comments beside variables instead of adding more categories.
   Keep required values active with `CHANGE_ME` placeholders. Comment out optional
   values that already have working Compose defaults so copying the example does
   not pin settings the user did not choose to change.
   Finish with `About this setup`. Link to upstream documentation, source, container image, release notes, license, support and security policy when available. Explain briefly which upstream example was followed and what this repository changed. Link to the upstream license instead of copying it.
   Decorative product logos are not required. Add a deployment-specific image
   under its `assets/` directory only when it explains a concrete instruction,
   expected result, architecture or workflow. Keep repository-wide media in
   `docs/assets/common/`. Use short descriptive alternative text, optimize images,
   sanitize screenshots and record the source, license and attribution when
   required. Do not create empty `docs/` or `assets/` directories.
6. Validate from the application directory:

   ```bash
   docker compose config --quiet
   docker compose --env-file .env.example config --quiet
   ```

   Omit the second command if there is no environment example. Supply temporary,
   non-secret test values where secrets are required. Also check documented
   extensions with the base file. Confirm that the base deployment still
   delivers its stated purpose without extensions. Avoid sharing resolved
   configuration containing real secrets.

   When a deployment exposes persistent source variables, validate the defaults
   and a representative absolute host path. Confirm that only the intended mount
   changes from `volume` to `bind` in `docker compose config`.

   ```bash
   docker compose -f compose.yaml \
     -f extensions/compose.<extension>.yaml config --quiet
   ```
7. Follow the quick start, verify a useful application action and persistence,
   and test restoration of sample data in an isolated deployment. Record what
   passed and what remains untested. Do not test on irreplaceable data.
8. Add a catalog link when the deployment is ready to list. Keep future requests
   in the [wishlist](docs/wishlist.md) rather than presenting them as supported.

## Pull request information

Include the purpose of the change, upstream references, commands used to verify
it, image version, host architecture and Docker/Compose versions. Explain changes
to storage, credentials, networking or upgrade behavior. Screenshots are optional.
Configuration-only submissions must clearly identify missing runtime checks.

Follow [SECURITY.md](SECURITY.md) for vulnerability reports. Never commit actual
`.env` files, private keys, runtime data or backups. The MIT repository license
covers contributions. Upstream applications and third-party assets retain their
own licensing.
