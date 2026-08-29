from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Show, Ticket


def index(request):
    shows = Show.objects.filter(is_active=True, date__gte=timezone.localdate())
    return render(request, 'stage/index.html', {'shows': shows})


def show_detail(request, slug):
    show = get_object_or_404(Show, slug=slug, is_active=True)
    return render(request, 'stage/show_detail.html', {'show': show})


@login_required
def reserve_ticket(request, slug):
    """Step 1: reserve seats for a show. Creates a ticket in 'pending_payment'."""
    show = get_object_or_404(Show, slug=slug, is_active=True)

    if request.method != 'POST':
        return redirect('show_detail', slug=slug)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 0

    if quantity < 1:
        messages.error(request, "Please select at least 1 ticket.")
        return redirect('show_detail', slug=slug)

    if show.is_past:
        messages.error(request, "This show has already taken place.")
        return redirect('show_detail', slug=slug)

    if quantity > show.tickets_remaining:
        messages.error(
            request,
            f"Sorry, only {show.tickets_remaining} ticket(s) left for this show."
        )
        return redirect('show_detail', slug=slug)

    with transaction.atomic():
        ticket = Ticket.objects.create(
            show=show,
            user=request.user,
            quantity=quantity,
            unit_price=show.price,
            total_amount=show.price * quantity,
        )

    return redirect('ticket_payment', ticket_code=ticket.ticket_code)


@login_required
def ticket_payment(request, ticket_code):
    """
    Step 2: pay first, then get the ticket.

    For now this is a manual confirmation step: the buyer pays out-of-band
    (M-Pesa / bank transfer) and submits their transaction reference here.
    Swap this out for a real payment gateway callback later -- it should
    call `ticket.mark_as_paid(reference=...)` the same way this view does.
    """
    ticket = get_object_or_404(Ticket, ticket_code=ticket_code, user=request.user)

    if ticket.status == Ticket.STATUS_PAID:
        return redirect('ticket_detail', ticket_code=ticket.ticket_code)

    if ticket.status == Ticket.STATUS_CANCELLED:
        messages.error(request, "This ticket reservation was cancelled.")
        return redirect('stage_home')

    if request.method == 'POST':
        reference = request.POST.get('payment_reference', '').strip()
        if not reference:
            messages.error(request, "Please enter your payment reference / transaction code.")
        else:
            ticket.mark_as_paid(reference=reference)
            messages.success(request, "Payment received! Your ticket is confirmed.")
            return redirect('ticket_detail', ticket_code=ticket.ticket_code)

    return render(request, 'stage/ticket_payment.html', {'ticket': ticket})


@login_required
def ticket_detail(request, ticket_code):
    ticket = get_object_or_404(Ticket, ticket_code=ticket_code, user=request.user)
    if ticket.status == Ticket.STATUS_PENDING:
        return redirect('ticket_payment', ticket_code=ticket.ticket_code)
    return render(request, 'stage/ticket_detail.html', {'ticket': ticket})


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('show')
    return render(request, 'stage/my_tickets.html', {'tickets': tickets})


@login_required
def cancel_ticket(request, ticket_code):
    ticket = get_object_or_404(Ticket, ticket_code=ticket_code, user=request.user)
    if request.method == 'POST' and ticket.status == Ticket.STATUS_PENDING:
        ticket.status = Ticket.STATUS_CANCELLED
        ticket.save()
        messages.info(request, "Reservation cancelled.")
    return redirect('my_tickets')
