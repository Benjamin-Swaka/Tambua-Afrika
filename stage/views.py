from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from . import pesapal
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


# ==============================================
# PESAPAL CHECKOUT
# ==============================================
# Additive: the manual "I've paid, here's my reference" form on
# ticket_payment.html still works exactly as before and stays as a
# fallback if Pesapal is ever unreachable. This just adds a "Pay with
# Pesapal" button that, when clicked, creates a hosted payment session
# and sends the buyer there instead.

@login_required
def pesapal_checkout(request, ticket_code):
    """POST-only: starts a Pesapal payment session for this ticket and
    redirects the buyer to Pesapal's hosted checkout page."""
    ticket = get_object_or_404(Ticket, ticket_code=ticket_code, user=request.user)

    if request.method != 'POST':
        return redirect('ticket_payment', ticket_code=ticket_code)

    if ticket.status != Ticket.STATUS_PENDING:
        return redirect('ticket_detail', ticket_code=ticket_code)

    full_name = (request.user.get_full_name() or request.user.username).split(' ', 1)
    first_name = full_name[0]
    last_name = full_name[1] if len(full_name) > 1 else ''

    billing_address = {
        "email_address": request.user.email,
        "phone_number": "",
        "country_code": "KE",
        "first_name": first_name,
        "middle_name": "",
        "last_name": last_name,
        "line_1": "",
        "line_2": "",
        "city": "",
        "state": "",
        "postal_code": "",
        "zip_code": "",
    }

    callback_url = f"{request.scheme}://{request.get_host()}{reverse('pesapal_callback')}"

    try:
        order = pesapal.submit_order(
            order_id=ticket.ticket_code,
            amount=ticket.total_amount,
            description=f"{ticket.quantity}x ticket - {ticket.show.title}"[:100],
            callback_url=callback_url,
            billing_address=billing_address,
        )
    except pesapal.PesapalError as exc:
        messages.error(
            request,
            "We couldn't start the Pesapal payment right now. You can still pay "
            "via M-Pesa/bank transfer below and enter your reference manually."
        )
        return redirect('ticket_payment', ticket_code=ticket_code)

    ticket.pesapal_tracking_id = order['order_tracking_id']
    ticket.save(update_fields=['pesapal_tracking_id'])

    return redirect(order['redirect_url'])


def pesapal_callback(request):
    """Browser is redirected here after the buyer finishes on Pesapal's
    hosted page. We re-verify with Pesapal server-side rather than
    trusting the query params (they aren't proof of payment on their own)."""
    tracking_id = request.GET.get('OrderTrackingId')
    merchant_reference = request.GET.get('OrderMerchantReference')

    if not tracking_id or not merchant_reference:
        return HttpResponseBadRequest("Missing Pesapal transaction reference.")

    ticket = get_object_or_404(Ticket, ticket_code=merchant_reference)

    try:
        status_data = pesapal.get_transaction_status(tracking_id)
    except pesapal.PesapalError:
        messages.error(request, "We couldn't confirm your payment status. Please contact us with your ticket code.")
        return redirect('ticket_payment', ticket_code=ticket.ticket_code)

    if pesapal.is_payment_successful(status_data):
        if not ticket.is_paid:
            ticket.mark_as_paid(reference=status_data.get('confirmation_code', tracking_id))
        messages.success(request, "Payment received! Your ticket is confirmed and the QR code has been emailed to you.")
        return redirect('ticket_detail', ticket_code=ticket.ticket_code)

    messages.error(request, "Your payment wasn't completed. You can try again below.")
    return redirect('ticket_payment', ticket_code=ticket.ticket_code)


@csrf_exempt
def pesapal_ipn(request):
    """
    Server-to-server notification -- may arrive even if the buyer closed
    their browser before the redirect back to pesapal_callback finished.
    Must always respond 200 with this exact JSON shape, using status:200
    (processed ok) or status:500 (received, but something went wrong on
    our end) inside the body -- see Pesapal's IPN docs.
    """
    tracking_id = request.GET.get('OrderTrackingId') or request.POST.get('OrderTrackingId')
    merchant_reference = request.GET.get('OrderMerchantReference') or request.POST.get('OrderMerchantReference')
    notification_type = request.GET.get('OrderNotificationType') or request.POST.get('OrderNotificationType', 'IPNCHANGE')

    response_body = {
        "orderNotificationType": notification_type,
        "orderTrackingId": tracking_id,
        "orderMerchantReference": merchant_reference,
        "status": 200,
    }

    if not tracking_id or not merchant_reference:
        response_body["status"] = 500
        return JsonResponse(response_body)

    try:
        ticket = Ticket.objects.get(ticket_code=merchant_reference)
        status_data = pesapal.get_transaction_status(tracking_id)
    except (Ticket.DoesNotExist, pesapal.PesapalError):
        response_body["status"] = 500
        return JsonResponse(response_body)

    if pesapal.is_payment_successful(status_data) and not ticket.is_paid:
        ticket.mark_as_paid(reference=status_data.get('confirmation_code', tracking_id))

    return JsonResponse(response_body)
