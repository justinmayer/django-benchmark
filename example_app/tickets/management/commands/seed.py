"""Seed the database with benchmark fixture data.

Invoked by the harness CLI via ``uv run benchmark setup``.
"""

from django.core.management.base import BaseCommand

from tickets.fixtures import create_data


class Command(BaseCommand):
    help = "Seed the database with benchmark fixture data."

    def handle(self, *args, **options):
        create_data()
        self.stdout.write(self.style.SUCCESS("Seeded benchmark fixture data."))
