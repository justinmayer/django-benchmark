"""Shared building blocks for scenario locustfiles.

Every scenario is a standalone locustfile under ``scenarios/`` that Locust
loads by path, with one scenario file per workload pattern."""

from locust import HttpUser, between


class BaseHttpUser(HttpUser):
    """Common base for benchmark users.

    ``wait_time`` paces task iterations; override it per-scenario for a
    different time intervals. Use ``@task`` weights to shape the workload mix.
    """

    # Pacing bounds in seconds between task iterations.
    wait_time = between(0.5, 2.0)

    # Base classes are subclassed and never spawned by Locust.
    abstract = True
