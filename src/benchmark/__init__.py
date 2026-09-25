from __future__ import annotations

import argparse
import http.client
import os
import shutil
import signal
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path.cwd()
EXAMPLE_APP = ROOT / "example_app"
RUNTIMES = ROOT / "runtimes"
SCENARIOS = ROOT / "scenarios"
RESULTS = ROOT / "results"

HEALTH_TIMEOUT = 30.0
STOP_TIMEOUT = 10.0


def load_profile(path: Path) -> dict:
    with path.open("rb") as file:
        return tomllib.load(file)


def run_manage(*args: str) -> None:
    manage = EXAMPLE_APP / "manage.py"
    if not manage.is_file():
        sys.exit(f"example_app manage.py is missing: {manage}")
    subprocess.check_call([sys.executable, str(manage), *args], cwd=EXAMPLE_APP)


def cmd_setup(*, seed: bool) -> None:
    print("Applying migrations...")
    run_manage("migrate", "--noinput")

    if seed:
        print("Seeding example data...")
        run_manage("seed")


def start_runtime(profile: dict, log_path: Path) -> subprocess.Popen:
    command = profile["command"]
    argv = [command, *profile.get("args", [])]
    cwd = ROOT / profile.get("cwd", ".")
    executable = shutil.which(command)
    if executable is None:
        sys.exit(
            f"{command!r} not found on PATH. "
            "Try: uv sync --extra gunicorn --extra example-app"
        )
    print(f"Starting runtime: {' '.join(argv)} (cwd={cwd})", flush=True)
    return subprocess.Popen(
        [executable, *argv[1:]],
        cwd=cwd,
        stdout=log_path.open("wb"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def health_alive(health_url: str) -> bool:
    """Return True if the health URL currently responds with a 2xx status.

    Network and protocol errors (server not up yet, timeouts, bad responses)
    count as "not healthy". A malformed URL raises ValueError: that is a
    configuration error and should surface, not be swallowed.
    """
    try:
        with urllib.request.urlopen(health_url, timeout=2) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, OSError, http.client.HTTPException):
        return False


def wait_for_health(
    proc: subprocess.Popen,
    health_url: str,
    timeout: float = HEALTH_TIMEOUT,
) -> bool:
    """Poll the health URL until it responds, the runtime exits, or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return False
        if health_alive(health_url):
            return True
        time.sleep(0.5)
    return False


def stop_runtime(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    print("Stopping runtime...", flush=True)
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=STOP_TIMEOUT)
    except subprocess.TimeoutExpired:
        print("Runtime did not stop; sending SIGKILL...")
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()


def print_log_tail(log_path: Path, lines: int = 20) -> None:
    print(f"--- {log_path.name} (last {lines} lines) ---")
    try:
        text = log_path.read_text().splitlines()
    except OSError:
        return
    print("\n".join(text[-lines:]))


def run_locust(
    scenario: str,
    host: str,
    users: int,
    duration: int,
    spawn_rate: float,
    report_dir: Path,
) -> int:
    locustfile = SCENARIOS / f"{scenario}.py"
    if not locustfile.is_file():
        sys.exit(f"Scenario file is missing: {locustfile}")

    argv = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        str(locustfile),
        "--headless",
        "-u",
        str(users),
        "-r",
        str(spawn_rate),
        "-t",
        f"{duration}s",
        "--host",
        host,
        "--html",
        str(report_dir / "report.html"),
        "--csv",
        str(report_dir / "run"),
    ]
    print(f"Running Locust: {' '.join(argv)}", flush=True)
    return subprocess.call(argv)


def cmd_run(
    scenario: str,
    runtime: str,
    launcher: str,
    users: int,
    duration: int,
    spawn_rate: float,
) -> None:
    if launcher == "docker":
        sys.exit("Docker launcher is not implemented yet.")

    profile_path = RUNTIMES / runtime / "profile.toml"
    if not profile_path.is_file():
        sys.exit(f"Runtime profile is missing: {profile_path}")

    profile = load_profile(profile_path)
    host = profile.get("host")
    health_url = profile.get("health_url")
    if not host or not health_url:
        sys.exit(f"profile.toml must define 'host' and 'health_url': {profile_path}")

    report_dir = RESULTS / runtime / scenario / datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    report_dir.mkdir(parents=True, exist_ok=True)

    if health_alive(health_url):
        sys.exit(
            f"Something is already serving {health_url}. Stop it first "
            "(e.g. pkill gunicorn / runserver) before running a benchmark."
        )

    proc = start_runtime(profile, report_dir / "runtime.log")
    try:
        if not wait_for_health(proc, health_url):
            print(f"Runtime never became healthy at {health_url} within {HEALTH_TIMEOUT:.0f}s")
            if proc.poll() is not None:
                print(f"Runtime exited early with code {proc.returncode}")
            print_log_tail(report_dir / "runtime.log")
            sys.exit(1)

        print(f"Runtime healthy at {health_url}", flush=True)
        exit_code = run_locust(scenario, host, users, duration, spawn_rate, report_dir)
    finally:
        stop_runtime(proc)

    print(f"Reports saved to: {report_dir}", flush=True)
    sys.exit(exit_code)


def cmd_compare() -> None:
    print(f"Would compare results in {RESULTS}")
    print("No result files yet; compare is a stub.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="benchmark",
        description="Django Benchmark profiles the performance of the Django web framework.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run a load scenario against a runtime")
    run.add_argument(
        "scenario",
        help="scenario name (locustfile under scenarios/, e.g. browse)",
    )
    run.add_argument(
        "--runtime",
        default="gunicorn-sync",
        help="runtime profile name (default: gunicorn-sync)",
    )
    run.add_argument(
        "--launcher",
        choices=("docker", "local"),
        default="local",
        help="how to start the runtime (default: local)",
    )
    run.add_argument(
        "-u", "--users",
        type=int,
        default=5,
        help="number of concurrent users (default: 5)",
    )
    run.add_argument(
        "-t", "--duration",
        type=int,
        default=30,
        help="run duration in seconds (default: 30)",
    )
    run.add_argument(
        "-r", "--spawn-rate",
        type=float,
        default=1.0,
        help="users spawned per second (default: 1.0)",
    )

    setup = sub.add_parser("setup", help="migrate and seed example_app")
    setup.add_argument(
        "--no-seed",
        action="store_true",
        help="only migrate; do not create fixture rows",
    )

    sub.add_parser("compare", help="compare result files (stub)")

    args = parser.parse_args()
    if args.command == "run":
        scenario = args.scenario.removesuffix(".py")
        cmd_run(
            scenario,
            args.runtime,
            args.launcher,
            args.users,
            args.duration,
            args.spawn_rate,
        )
    elif args.command == "setup":
        cmd_setup(seed=not args.no_seed)
    elif args.command == "compare":
        cmd_compare()
