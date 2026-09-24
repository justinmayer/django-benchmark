from django.db import models
from django.contrib.auth.models import User


NEEDS_TRIAGE = "NEEDS_TRIAGE"
NEEDS_PR = "NEEDS_PR"
NEEDS_PR_REVIEW = "NEEDS_PR_REVIEW"
WAITING_ON_AUTHOR = "WAITING_ON_AUTHOR"
READY_FOR_CHECKIN = "READY_FOR_CHECKIN"
CLOSED = "CLOSED"


QUEUE_CHOICES = {
    NEEDS_TRIAGE: "Needs Triage",
    NEEDS_PR: "Needs PR",
    NEEDS_PR_REVIEW: "Needs PR Review",
    WAITING_ON_AUTHOR: "Waiting on Author",
    READY_FOR_CHECKIN: "Ready for Checkin",
    CLOSED: "Closed",
}


class Component(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='tickets')
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tickets')
    reporter = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reported_tickets')
    queue = models.CharField(
        max_length=20,
        choices=QUEUE_CHOICES,
        default=NEEDS_TRIAGE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.ticket.title}"


class PullRequest(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='pull_requests')
    pr_number = models.CharField(max_length=100)
    pr_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PR #{self.pr_number} for {self.ticket.title}"
