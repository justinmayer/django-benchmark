"""Browse scenario — read-heavy ticket browsing.

Requests (grouped in Locust stats under ``browse:*``):

- ``browse:list``   GET /tickets/
- ``browse:detail`` GET /tickets/<id>/
"""

from locust import task

from common.base import BaseHttpUser

# Ticket ID seeded by `manage.py seed` (tickets/fixtures.create_data).
TICKET_ID = 1


class BrowseUser(BaseHttpUser):
    """A user browsing the ticket tracker (read-heavy)."""

    @task(2)
    def ticket_list(self) -> None:
        resp = self.client.get("/tickets/", name="browse:list")
        resp.raise_for_status()

    @task(1)
    def ticket_detail(self) -> None:
        resp = self.client.get(f"/tickets/{TICKET_ID}/", name="browse:detail")
        resp.raise_for_status()
