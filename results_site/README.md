# Results site

[Pelican](https://getpelican.com/) project that renders `data/table.json` as static HTML.

## Setup

From the repo root:

```bash
uv sync --extra results-site
```

## Build

```bash
uv run benchmark preprocess
uv run pelican --settings results_site/pelicanconf.py
```

Output is `results_site/output/`. Preview with:

```bash
uv run pelican --listen --settings results_site/pelicanconf.py
```

The index groups by runtime. Under each runtime, each scenario has a short description of its workload, then a row per concurrent user count. The usual counts are 10, 100, and 1000; any other count present in a published run is shown too.

`uv run benchmark preprocess` reads each `results/published/<runtime>/<scenario>/<timestamp>/` directory and writes `results_site/data/table.json`. That file is the table: runtimes, then scenarios, then a row per concurrent user count (10, 100, 1000, plus any other count that was published). Numbers are the Aggregated row of `run_stats.csv` (requests/s, average response time, p50, p95, p99) and the peak user count from `run_stats_history.csv`. Pelican only reads the JSON file.

Copy the latest local run into `results/published/` with `uv run benchmark save-results`. Other files under `results/` stay gitignored.
