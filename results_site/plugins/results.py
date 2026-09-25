from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pelican import signals


@dataclass(frozen=True)
class RunResult:
    name: str
    source: str
    runtime: str | None
    launcher: str | None
    django_version: str | None
    rps: float | None
    p50_ms: float | None
    p99_ms: float | None
    errors: int | None
    raw: dict


def _read_json(path: Path) -> RunResult | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        data = {"value": data}
    return RunResult(
        name=path.stem,
        source=str(path),
        runtime=data.get("runtime"),
        launcher=data.get("launcher"),
        django_version=data.get("django_version"),
        rps=data.get("rps"),
        p50_ms=data.get("p50_ms"),
        p99_ms=data.get("p99_ms"),
        errors=data.get("errors"),
        raw=data,
    )


def load_runs(settings: dict) -> list[RunResult]:
    dirs = [
        Path(settings["BENCHMARK_RESULTS_DIR"]),
        Path(settings["SAMPLE_RESULTS_DIR"]),
    ]
    runs: list[RunResult] = []
    seen: set[str] = set()
    for directory in dirs:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            if path.name in seen:
                continue
            result = _read_json(path)
            if result is None:
                continue
            seen.add(path.name)
            runs.append(result)
    return runs


def add_runs(generator) -> None:
    generator.context["runs"] = load_runs(generator.settings)


def register() -> None:
    signals.generator_init.connect(add_runs)
