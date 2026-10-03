# Results site

[Pelican](https://getpelican.com/) project that turns benchmark CSV into static HTML.

## Setup

From the repo root:

```bash
uv sync --extra results-site
```

## Build

```bash
uv run pelican --settings results_site/pelicanconf.py
```

Output is `results_site/output/`. Preview with:

```bash
uv run pelican --listen --settings results_site/pelicanconf.py
```

CSV files in `results/published/` (and subfolders) are listed on the index. Copy the latest local run there with `uv run benchmark save-results`. Other files under `results/` stay gitignored.
