from __future__ import annotations

from pathlib import Path

from pelican import signals

from benchmark.preprocess import read_table


def format_metric(value: float | None) -> str:
    if value is None:
        return "—"
    rendered = f"{value:.2f}".rstrip("0").rstrip(".")
    return rendered or "0"


def add_scenarios(generator) -> None:
    path = Path(generator.settings["BENCHMARK_TABLE"])
    generator.context["runtimes"] = read_table(path)
    generator.env.filters["metric"] = format_metric


def register() -> None:
    signals.generator_init.connect(add_scenarios)
