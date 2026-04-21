from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, TicketMessage


@login_required
def ticket_list(request):
    """List the current user's support tickets."""
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, "support/ticket_list.html", {"tickets": tickets})


@login_required
def ticket_create(request):
    """Create a new support ticket."""
    if request.method == "POST":
        ticket = Ticket.objects.create(
            user=request.user,
            email=request.user.email,
            subject=request.POST.get("subject", ""),
            category=request.POST.get("category", "general"),
            priority=request.POST.get("priority", "medium"),
        )
        body = request.POST.get("body", "")
        if body:
            TicketMessage.objects.create(ticket=ticket, author=request.user, body=body)
        messages.success(request, f"Ticket {ticket.ticket_number} created.")
        return redirect("support:ticket_detail", ticket_number=ticket.ticket_number)
    return render(request, "support/ticket_create.html")


@login_required
def ticket_detail(request, ticket_number):
    """View ticket details and add replies."""
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number, user=request.user)
    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            TicketMessage.objects.create(ticket=ticket, author=request.user, body=body)
            messages.success(request, "Reply added.")
        return redirect("support:ticket_detail", ticket_number=ticket.ticket_number)
    return render(request, "support/ticket_detail.html", {
        "ticket": ticket,
        "ticket_messages": ticket.messages.all(),
    })
