from django import forms
from tickets.models import Ticket


class TicketForm(forms.Form):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'component', 'assignee', 'reporter', 'queue']
