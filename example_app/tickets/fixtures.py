from tickets.models import Component, Ticket, Comment, PullRequest
from tickets.constants import NEEDS_TRIAGE, READY_FOR_CHECKIN

def create_data():
    # Create components
    component1 = Component.objects.create(name="Component 1", description="Description for Component 1")
    component2 = Component.objects.create(name="Component 2", description="Description for Component 2")

    # Create tickets
    ticket1 = Ticket.objects.create(title="Ticket 1", description="Description for Ticket 1", component=component1, queue=NEEDS_TRIAGE)
    ticket2 = Ticket.objects.create(title="Ticket 2", description="Description for Ticket 2", component=component2, queue=READY_FOR_CHECKIN)

    # Create comments
    Comment.objects.create(ticket=ticket1, author="User A", content="Comment for Ticket 1")
    Comment.objects.create(ticket=ticket2, author="User B", content="Comment for Ticket 2")

    # Create pull requests
    PullRequest.objects.create(ticket=ticket1, pr_number=35894)
    PullRequest.objects.create(ticket=ticket2, pr_number=37365)
