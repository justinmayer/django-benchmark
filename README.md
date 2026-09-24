# Django Benchmark

The objective of this project is to benchmark and profile the performance of the [Django web framework](https://www.djangoproject.com).

## Layout

- `src/benchmark/` — harness CLI (`benchmark`)
- `example_app/` — Django project under test
- `runtimes/` — named server profiles (how the app is started)
- `constraints/` — Django version pins for a future matrix
- `results/` — benchmark output (gitignored)

## Setup

```bash
uv sync --extra gunicorn --extra example-app
uv run benchmark setup
```

That installs extras, applies `example_app` migrations, and runs `manage.py seed` (that command is not implemented yet). Use `--no-seed` to migrate only.

Gunicorn and Django are optional extras. Locust is a default dependency. Running Locust is not implemented yet.

## Commands

```bash
uv run benchmark setup
uv run benchmark run gunicorn-sync
uv run benchmark run gunicorn-sync --launcher local
uv run benchmark run gunicorn-sync --launcher docker
uv run benchmark compare
```

`--launcher local` starts gunicorn from `runtimes/<name>/profile.toml` (cwd `example_app`). Docker and `compare` are not implemented yet.
