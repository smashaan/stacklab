<img src="../../docs/assets/latex/latex_logo.svg" alt="LaTeX logo" width="150">

# LaTeX

Compile LaTeX projects without installing TeX Live on the host. A disposable compiler container reads a host workspace and writes the PDF beside its sources.

## Supported setup

- Island of TeX's full `texlive/texlive:latest` image, including common build helpers but not the documentation tree.
- One-shot `latexmk` compilation with pdfLaTeX. The container exits when compilation finishes.
- A bind-mounted workspace so source and output remain directly accessible.
- Network disabled, read-only container filesystem, dropped Linux capabilities and host UID/GID mapping by default.

The upstream `latest` image is rebuilt regularly and can change when pulled. Its maintainers publish dated tags for reproducible builds. Smaller schemes and images containing TeX documentation or sources are outside this repository's maintained configuration.

## Before you start

- Docker Engine and the Docker Compose plugin (`docker compose`).
- Enough disk space for the full TeX Live image.
- A Linux account that can write to the workspace. Defaults are UID and GID `1000`.
- ARMv8 images are described by upstream as experimental and are not tested here.

LaTeX input is executable document-processing input, not passive text. Do not compile untrusted projects based only on the container restrictions. The workspace remains writable, and enabling `-shell-escape` lets documents start programs present in the image.

## Quick start

`.env` is optional. The included example works with the defaults:

```bash
cd apps/latex
docker compose run --rm latex
```

Open `workspace/main.pdf`. Success exits with status zero and reports `Output written on main.pdf`. Replace `workspace/main.tex` with your project or select another directory below. Generated files in the included workspace are ignored by Git.

## Compile a project

The default command is `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`. Override it after the service name:

```bash
# Another root document with pdfLaTeX
docker compose run --rm latex latexmk -pdf -interaction=nonstopmode -halt-on-error report.tex

# LuaLaTeX
docker compose run --rm latex latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex

# Remove latexmk-generated build files
docker compose run --rm latex latexmk -C
```

`latexmk` determines the necessary passes and bibliography steps from the project.

## Configuration

```bash
cp .env.example .env
# Edit .env, then inspect the resolved mount and user.
docker compose config
```

| Variable | Default | Purpose |
|---|---|---|
| `LATEX_WORKSPACE_SOURCE` | `./workspace` | Host directory mounted read-write at `/workdir` |
| `LATEX_USER_ID` | `1000` | Linux user ID that runs the compiler and owns output |
| `LATEX_GROUP_ID` | `1000` | Linux group ID that runs the compiler and owns output |

Find the current IDs with `id -u` and `id -g`. Use an absolute workspace path for a project elsewhere. Relative paths resolve from this app directory.

> [!WARNING]
> Changing the workspace does not copy files. Inspect the resolved `/workdir` mount before compiling. It is writable by the document processor, so never select a broad or sensitive path.

## Your data

| Source | Container path | Contents | Backup need |
|---|---|---|---|
| `LATEX_WORKSPACE_SOURCE` | `/workdir` | Sources, figures, bibliography and generated output | Back up sources and non-reproducible assets |
| In-memory temporary filesystem | `/tmp` | Per-run caches and temporary files | None |

There is no application volume or database. The container is removed after each run. Keep sources in version control and normal host backups. PDFs and auxiliary files can usually be rebuilt.

## Back up and restore

Back up the selected workspace with the same version-control and file-backup process used for other documents. Include every source, local class or style file, bibliography, figure and other asset that cannot be downloaded reproducibly.

To verify recovery, restore the workspace to a different directory, point `LATEX_WORKSPACE_SOURCE` at it and run the normal compile command. Open the resulting PDF and compare representative pages. Generated auxiliary files do not need restoration when the project builds successfully from source.

## Update and reproducibility

Review the upstream image changes, then update and test:

```bash
docker compose pull latex
docker compose run --rm latex
docker compose images
```

Inspect representative output before accepting a toolchain change. For reproducible production documents, replace `latest` in `compose.yaml` with a tested upstream `TL<release>-<date>` tag and record it with the project. Maintaining that pin then becomes the project owner's responsibility.

## Troubleshooting

| Symptom | Check / action |
|---|---|
| Output has the wrong owner | Set `LATEX_USER_ID` and `LATEX_GROUP_ID` from `id -u` and `id -g`. |
| `main.tex` is missing | Check `LATEX_WORKSPACE_SOURCE` and the resolved `/workdir` mount. |
| A package or font is unavailable | Confirm compatibility with current TeX Live. Pin a working dated image if an update regressed. |
| A download fails while compiling | Network access is disabled. Put required assets in the workspace first. |
| A tool cannot write outside the workspace | Configure it to use `/workdir` or `/tmp`. The container root is read-only. |
| Compilation stops without a PDF | Read the first error in the console or `.log`. `-halt-on-error` exposes failures to automation. |

For general commands, see [shared troubleshooting](../../docs/troubleshooting.md).

## About this setup

The maintained Island of TeX image replaces the earlier Debian Bullseye build and incorrect `postgres-data` mount. Compose acts as a repeatable command runner instead of keeping an idle shell container alive. No custom Dockerfile is required.

- [TeX Live website and current release](https://tug.org/texlive/)
- [TeX Live 2026 guide](https://tug.org/texlive/doc/texlive-en/texlive-en.html)
- [Island of TeX image documentation](https://github.com/islandoftex/texlive)
- [Container image](https://hub.docker.com/r/texlive/texlive)
- [Image source and issue tracker](https://gitlab.com/islandoftex/images/texlive)
- [LaTeX source repository](https://github.com/latex3/latex2e)
- [TeX Live licensing](https://tug.org/texlive/copying.html)
