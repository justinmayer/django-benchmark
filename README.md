# Django Benchmark

The objective of this project is to benchmark and profile the performance of the [Django web framework](https://www.djangoproject.com).

## Layout

- `src/benchmark/` — harness CLI (`benchmark`)
- `example_app/` — Django project under test
- `scenarios/` — Locust load-test files (workload patterns)
- `runtimes/` — named server profiles (how the app is started)
- `constraints/` — Django version pins for a future matrix
- `results/` — benchmark output (gitignored)
- `results_site/` — Pelican project that builds those results into static HTML

## Setup

```bash
uv sync --extra gunicorn --extra example-app
uv run benchmark setup
```

That installs extras, applies `example_app` migrations, and runs `manage.py seed`. Use `--no-seed` to migrate only.

## Run a benchmark

`benchmark run` starts the runtime from `runtimes/<name>/profile.toml`, waits for its `health_url`, runs the scenario headless, and saves reports under `results/<runtime>/<scenario>/<timestamp>/`:

```bash
uv run benchmark run browse --runtime gunicorn-sync -u 20 -t 120 -r 2
```

To run a scenario without automatically spawning the runtime, point Locust at a running server:

```bash
uv run locust -f scenarios/browse.py --headless -u 5 -t 15s --host http://127.0.0.1:8000 --html results/smoke/browse.html --csv results/smoke/browse
```

## Commands

```bash
uv run benchmark setup
uv run benchmark run browse --runtime gunicorn-sync
uv run benchmark run browse --launcher local
uv run benchmark run browse --launcher docker
uv run benchmark compare
```

`--launcher local` (the default) starts the runtime from `runtimes/<name>/profile.toml` (cwd `example_app`). Docker and `compare` are not implemented yet.

## Results site

Pelican is an optional extra on the same lockfile. It does not use Django, so it does not conflict with the `example-app` Django pin.

```bash
uv sync --extra results-site
uv run pelican --settings results_site/pelicanconf.py
```

See [`results_site/README.md`](results_site/README.md).
