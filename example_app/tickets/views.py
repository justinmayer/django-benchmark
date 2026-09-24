from django.shortcuts import render, redirect
from .models import Ticket
from .forms import TicketForm


def ticket_list(request):
    tickets = Ticket.objects.all()
    return render(request, 'tickets/tickets_list.html', {'tickets': tickets})


def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ticket-list')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_create.html', {'form': form})


def ticket_detail(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})
