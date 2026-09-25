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

CSV files in repo-root `results/*.csv` are listed on the index. Sample rows live in `data/` so the table is not empty before real benchmarks exist.
