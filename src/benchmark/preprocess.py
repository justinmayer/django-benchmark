"""Turn published Locust runs into the results table.

``write_table`` reads ``results/published/<runtime>/<scenario>/<timestamp>/``
and writes one JSON file. The site reads that file and does not parse Locust
CSVs itself. Each run currently contributes the Aggregated row from
``run_stats.csv``, labeled with the highest user count in
``run_stats_history.csv``. Replace :func:`summarize_run` when a steadier
window should feed the same file.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

# Sub-rows every scenario gets. A published run at another user count is
# included as well, so partial data still appears.
EXPECTED_USER_COUNTS = (10, 100, 1000)

WORKLOADS = {
    "browse": "Read-heavy ticket browsing: GET /tickets/ and GET /tickets/<id>/.",
}

_PERCENTILE_FIELDS = (
    ("50%", "p50_ms"),
    ("95%", "p95_ms"),
    ("99%", "p99_ms"),
)


@dataclass(frozen=True)
class RunMetrics:
    runtime: str
    scenario: str
    timestamp: str
    users: int | None
    requests_per_second: float | None
    average_response_time_ms: float | None
    p50_ms: float | None
    p95_ms: float | None
    p99_ms: float | None


@dataclass(frozen=True)
class ScenarioResults:
    """Latest published run for each user count of one workload and runtime."""

    runtime: str
    scenario: str
    runs: tuple[RunMetrics, ...]


def _float(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    if not text or text == "N/A":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _peak_users(history: Path) -> int | None:
    if not history.is_file():
        return None
    peak: int | None = None
    try:
        with history.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                if row.get("Name") != "Aggregated":
                    continue
                count = _float(row.get("User Count"))
                if count is None:
                    continue
                users = int(count)
                peak = users if peak is None else max(peak, users)
    except OSError:
        return peak
    return peak


def _aggregated_row(stats_path: Path) -> dict[str, str] | None:
    try:
        with stats_path.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                if row.get("Name") == "Aggregated":
                    return row
    except OSError:
        return None
    return None


def summarize_run(run_dir: Path, published: Path) -> RunMetrics | None:
    """Read one ``<published>/<runtime>/<scenario>/<timestamp>/`` directory."""
    stats_path = run_dir / "run_stats.csv"
    if not stats_path.is_file():
        return None
    try:
        relative = run_dir.relative_to(published)
    except ValueError:
        return None
    if len(relative.parts) != 3:
        return None
    runtime, scenario, timestamp = relative.parts

    aggregated = _aggregated_row(stats_path)
    if aggregated is None:
        return None

    percentiles = {
        field: _float(aggregated.get(column)) for column, field in _PERCENTILE_FIELDS
    }
    return RunMetrics(
        runtime=runtime,
        scenario=scenario,
        timestamp=timestamp,
        users=_peak_users(run_dir / "run_stats_history.csv"),
        requests_per_second=_float(aggregated.get("Requests/s")),
        average_response_time_ms=_float(aggregated.get("Average Response Time")),
        p50_ms=percentiles["p50_ms"],
        p95_ms=percentiles["p95_ms"],
        p99_ms=percentiles["p99_ms"],
    )


def load_runs(published: Path) -> list[RunMetrics]:
    """Every published run. Several timestamps for one user count are all returned."""
    if not published.is_dir():
        return []
    runs: list[RunMetrics] = []
    for stats_path in sorted(published.rglob("run_stats.csv")):
        summary = summarize_run(stats_path.parent, published)
        if summary is not None:
            runs.append(summary)
    return runs


def load_scenarios(published: Path) -> list[ScenarioResults]:
    """Group runs by runtime and scenario. The latest timestamp wins per user count."""
    latest: dict[tuple[str, str, int | None], RunMetrics] = {}
    for run in load_runs(published):
        key = (run.runtime, run.scenario, run.users)
        current = latest.get(key)
        if current is None or run.timestamp > current.timestamp:
            latest[key] = run

    grouped: dict[tuple[str, str], list[RunMetrics]] = {}
    for run in latest.values():
        grouped.setdefault((run.runtime, run.scenario), []).append(run)

    scenarios: list[ScenarioResults] = []
    for runtime, scenario in sorted(grouped, key=lambda item: (item[1], item[0])):
        runs = tuple(sorted(grouped[(runtime, scenario)], key=_users_sort_key))
        scenarios.append(ScenarioResults(runtime=runtime, scenario=scenario, runs=runs))
    return scenarios


def _users_sort_key(run: RunMetrics) -> tuple[int, int]:
    if run.users is None:
        return (1, 0)
    return (0, run.users)


@dataclass(frozen=True)
class TableLevel:
    users: int | None
    requests_per_second: float | None
    average_response_time_ms: float | None
    p50_ms: float | None
    p95_ms: float | None
    p99_ms: float | None


@dataclass(frozen=True)
class TableScenario:
    name: str
    description: str
    levels: tuple[TableLevel, ...]


@dataclass(frozen=True)
class TableRuntime:
    name: str
    scenarios: tuple[TableScenario, ...]


def _table_level(users: int | None, run: RunMetrics | None) -> TableLevel:
    if run is None:
        return TableLevel(users, None, None, None, None, None)
    return TableLevel(
        users=users,
        requests_per_second=run.requests_per_second,
        average_response_time_ms=run.average_response_time_ms,
        p50_ms=run.p50_ms,
        p95_ms=run.p95_ms,
        p99_ms=run.p99_ms,
    )


def _scenario_table(group: ScenarioResults) -> TableScenario:
    by_users = {run.users: run for run in group.runs}
    user_counts = set(EXPECTED_USER_COUNTS)
    user_counts.update(count for count in by_users if count is not None)
    levels = [_table_level(count, by_users.get(count)) for count in sorted(user_counts)]
    if None in by_users:
        levels.append(_table_level(None, by_users[None]))
    workload = WORKLOADS.get(group.scenario, group.scenario.replace("-", " "))
    return TableScenario(name=group.scenario, description=workload, levels=tuple(levels))


def build_table(published: Path) -> list[TableRuntime]:
    """One group per runtime, then one scenario, then a row per user count."""
    by_runtime: dict[str, list[TableScenario]] = {}
    for group in load_scenarios(published):
        by_runtime.setdefault(group.runtime, []).append(_scenario_table(group))

    return [
        TableRuntime(name=runtime, scenarios=tuple(sorted(scenarios, key=lambda item: item.name)))
        for runtime, scenarios in sorted(by_runtime.items())
    ]


def write_table(published: Path, destination: Path) -> Path:
    payload = {"runtimes": [asdict(runtime) for runtime in build_table(published)]}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def read_table(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("runtimes", [])
