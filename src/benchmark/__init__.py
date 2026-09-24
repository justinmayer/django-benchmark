from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
EXAMPLE_APP = ROOT / "example_app"
RUNTIMES = ROOT / "runtimes"
RESULTS = ROOT / "results"


def run_locust() -> None:
    # Locust is installed as a default dependency. Wiring a real locustfile
    # comes after the harness is wired to example_app.
    # TODO: locust -f ... --host ...
    raise NotImplementedError("locust")


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

    setup = sub.add_parser("setup", help="migrate and seed example_app")
    setup.add_argument(
        "--no-seed",
        action="store_true",
        help="only migrate; do not create fixture rows",
    )

    sub.add_parser("compare", help="compare result files (stub)")

    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args.runtime, args.launcher)
    elif args.command == "setup":
        cmd_setup(seed=not args.no_seed)
    elif args.command == "compare":
        cmd_compare()
