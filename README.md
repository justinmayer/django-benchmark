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
uv sync --extra gunicorn
```

Gunicorn is an optional extra. Locust is a default dependency. Running Locust is not implemented yet.

## Commands

```bash
uv run benchmark run gunicorn-sync --launcher local
uv run benchmark run gunicorn-sync --launcher docker
uv run benchmark compare
```

`run` and `compare` are stubs: they do not start gunicorn or Locust yet.
