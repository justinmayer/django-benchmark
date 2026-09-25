from __future__ import annotations

import csv
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


def _blank(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _float(value: str | None) -> float | None:
    value = _blank(value)
    if value is None:
        return None
    return float(value)


def _int(value: str | None) -> int | None:
    value = _blank(value)
    if value is None:
        return None
    return int(float(value))


def _read_csv(path: Path) -> list[RunResult]:
    runs: list[RunResult] = []
    try:
        with path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
    except OSError:
        return []
    for index, row in enumerate(rows, start=1):
        name = _blank(row.get("name")) or (
            path.stem if len(rows) == 1 else f"{path.stem}-{index}"
        )
        try:
            runs.append(
                RunResult(
                    name=name,
                    source=str(path),
                    runtime=_blank(row.get("runtime")),
                    launcher=_blank(row.get("launcher")),
                    django_version=_blank(row.get("django_version")),
                    rps=_float(row.get("rps")),
                    p50_ms=_float(row.get("p50_ms")),
                    p99_ms=_float(row.get("p99_ms")),
                    errors=_int(row.get("errors")),
                )
            )
        except (TypeError, ValueError):
            continue
    return runs


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
        for path in sorted(directory.glob("*.csv")):
            if path.name in seen:
                continue
            seen.add(path.name)
            runs.extend(_read_csv(path))
    return runs


def add_runs(generator) -> None:
    generator.context["runs"] = load_runs(generator.settings)


def register() -> None:
    signals.generator_init.connect(add_runs)
