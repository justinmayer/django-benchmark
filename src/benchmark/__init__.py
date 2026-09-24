from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path.cwd()
RUNTIMES = ROOT / "runtimes"
RESULTS = ROOT / "results"


def run_locust() -> None:
    # Locust is installed as a default dependency. Wiring a real locustfile
    # comes after the harness is wired to example_app.
    # TODO: locust -f ... --host ...
    raise NotImplementedError("locust")


def cmd_run(runtime: str, launcher: str) -> None:
    profile = RUNTIMES / runtime / "profile.toml"
    print(f"Would run runtime {runtime!r} with launcher {launcher!r}")
    print(f"Profile: {profile}")
    if not profile.is_file():
        print("Profile file is missing; add it under runtimes/<name>/profile.toml")
        return
    print("Not starting gunicorn yet.")
    run_locust()


def cmd_compare() -> None:
    print(f"Would compare results in {RESULTS}")
    print("No result files yet; compare is a stub.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="benchmark",
        description="Django Benchmark profiles the performance of the Django web framework.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run a runtime profile (stub)")
    run.add_argument("runtime", help="runtime profile name (e.g. gunicorn-sync)")
    run.add_argument(
        "--launcher",
        choices=("docker", "local"),
        default="docker",
        help="how to start the runtime (default: docker)",
    )

    sub.add_parser("compare", help="compare result files (stub)")

    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args.runtime, args.launcher)
    elif args.command == "compare":
        cmd_compare()
