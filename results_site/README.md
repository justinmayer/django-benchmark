# Results site

[Pelican](https://getpelican.com/) project that turns benchmark JSON into static HTML.

Pelican is a root optional extra (`results-site`). It does not depend on Django, so it shares the repo `uv.lock` and does not conflict with the Django pin used to run `example_app`.

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

JSON files in repo-root `results/*.json` are listed on the index. Sample rows live in `data/` so the table is not empty before real benchmarks exist.
