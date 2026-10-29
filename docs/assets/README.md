# Documentation assets

Store small images used by repository documentation in this directory.

## Layout

```text
assets/
├── common/                       # Repository-wide images
└── application-name/             # Images for one app or stack
    ├── application-name_logo.svg
    ├── application-name_dashboard.png
    └── application-name_architecture.svg
```

Keep each app or stack directory flat until more organization is useful. Use lowercase, hyphenated names. Existing filenames can remain stable when renaming them would only create noisy changes.

Prefer SVG for logos and diagrams. Use an optimized PNG when SVG is unavailable or when the image is a screenshot. Keep screenshots small enough to review in Git while preserving readable text.

Prefer official project assets. Record the source and license when attribution is required. Do not assume that an open source application license automatically covers its logo or trademark.

Reuse an existing repository asset when one is already available. Otherwise, check [Dashboard Icons](https://dashboardicons.com/) when an official project asset is not readily available. Download the file into this repository instead of embedding a CDN URL. Verify the individual icon's source, license and trademark conditions before use.

Every Markdown or HTML image must have short, useful alternative text. For example:

```html
<img src="../../docs/assets/adminer/adminer_logo.svg" alt="Adminer logo" width="150">
```

Do not include credentials, private domains, internal IP addresses or personal data in screenshots.
