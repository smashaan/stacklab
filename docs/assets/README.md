# Shared documentation assets

Store only repository-wide images and media used by multiple deployments in this directory. Deployment-specific screenshots and diagrams belong beside their deployment under `apps/<name>/assets/`.

## Layout

```text
assets/
└── common/                       # Repository-wide images
    ├── stacklab_logo.svg
    └── repository-architecture.svg
```

Do not mirror the `apps/` hierarchy here. A deployment that needs explanatory media creates its own optional `assets/` directory. Keep that directory flat until more organization is genuinely useful and use lowercase, hyphenated filenames.

Prefer SVG for repository branding and diagrams. Use an optimized PNG when SVG is unavailable or when the image is a screenshot. Keep screenshots small enough to review in Git while preserving readable text.

Record the source and license when attribution is required. Do not assume that an open source application license automatically covers its logo, trademark, screenshot or other media.

Do not add decorative product logos merely to brand deployment READMEs. Link to an upstream demonstration instead of copying a gallery. Do not embed remote images whose content or availability is outside this repository's control.

Every Markdown or HTML image must have short, useful alternative text. For example:

```markdown
![Proxy network architecture](assets/proxy-network.svg)
```

Do not include credentials, private domains, internal IP addresses or personal data in screenshots.
