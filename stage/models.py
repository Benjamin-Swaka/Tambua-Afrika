import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Show(models.Model):
    """A live performance / production that tickets can be sold for."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField(blank=True)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=100)
    image = models.ImageField(upload_to='stage/shows/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.title} - {self.date}"

    def get_absolute_url(self):
        return reverse('show_detail', kwargs={'slug': self.slug})

    @property
    def is_past(self):
        return self.date < timezone.localdate()

    @property
    def tickets_reserved(self):
        """Seats currently held: paid tickets plus ones still awaiting payment."""
        agg = self.tickets.filter(
            status__in=[Ticket.STATUS_PENDING, Ticket.STATUS_PAID]
        ).aggregate(total=models.Sum('quantity'))
        return agg['total'] or 0

    @property
    def tickets_remaining(self):
        return max(self.capacity - self.tickets_reserved, 0)

    @property
    def is_sold_out(self):
        return self.tickets_remaining <= 0


class Ticket(models.Model):
    """
    A ticket reservation for a Show.

    Flow (manual, for now): user reserves seats -> status starts as
    'pending_payment' -> user pays out-of-band (M-Pesa/bank) and submits a
    reference -> ticket is marked 'paid' and becomes their valid ticket.

    When automatic checkout (a real payment gateway) is added later, that
    integration should call `mark_as_paid()` from its webhook/callback
    instead of the manual reference form in `ticket_payment` view.
    """

    STATUS_PENDING = 'pending_payment'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Awaiting Payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    ticket_code = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_reference = models.CharField(
        max_length=100, blank=True,
        help_text="M-Pesa code or bank reference supplied by the buyer."
    )
    pesapal_tracking_id = models.CharField(
        max_length=100, blank=True,
        help_text="Pesapal's OrderTrackingId for this payment, if paid via Pesapal.",
    )
    qr_code = models.ImageField(upload_to='stage/tickets/qrcodes/', blank=True, null=True)
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tickets_checked_in',
        help_text="Which staff member scanned/checked this ticket in at the door.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_code} - {self.show.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = self._generate_code()
        if not self.total_amount:
            self.total_amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_code():
        return f"TAS-{uuid.uuid4().hex[:10].upper()}"

    def mark_as_paid(self, reference=''):
        """
        Called by both the manual reference form AND the Pesapal
        callback/IPN handlers -- whichever confirms payment first wins.
        Generates the check-in QR code and emails it on the transition
        into 'paid' (not on every call, so a duplicate IPN retry doesn't
        re-send the email or regenerate the QR).
        """
        already_paid = self.status == self.STATUS_PAID
        self.status = self.STATUS_PAID
        self.paid_at = self.paid_at or timezone.now()
        if reference:
            self.payment_reference = reference
        if not self.qr_code:
            self._generate_qr_code()
        self.save()
        if not already_paid:
            self._send_ticket_confirmation_email()

    def _verify_url(self):
        path = reverse('admin_ticket_verify_code', kwargs={'ticket_code': self.ticket_code})
        return f"{settings.SITE_BASE_URL}{path}"

    def _generate_qr_code(self):
        """
        Encodes the door-verification URL (not just the bare ticket
        code) so scanning it with any phone camera opens straight to
        the admin check-in page. That page itself requires a staff
        login, so the QR image alone isn't enough to fake a check-in --
        it just saves an admin from typing the code by hand.
        """
        import qrcode
        from io import BytesIO
        from django.core.files.base import ContentFile

        img = qrcode.make(self._verify_url())
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        self.qr_code.save(f"{self.ticket_code}.png", ContentFile(buffer.getvalue()), save=False)

    def _send_ticket_confirmation_email(self):
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from email.mime.image import MIMEImage

        context = {'ticket': self, 'verify_url': self._verify_url()}
        text_body = render_to_string('emails/ticket_confirmation.txt', context)
        html_body = render_to_string('emails/ticket_confirmation.html', context)

        email = EmailMultiAlternatives(
            subject=f"Your ticket for {self.show.title} — {self.ticket_code}",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.user.email],
        )
        email.attach_alternative(html_body, 'text/html')
        email.mixed_subtype = 'related'  # lets the inline <img cid:...> render in the HTML body

        if self.qr_code:
            self.qr_code.open('rb')
            qr_bytes = self.qr_code.read()
            self.qr_code.close()

            # Inline (renders inside the email body via cid:qr_code)
            inline_image = MIMEImage(qr_bytes)
            inline_image.add_header('Content-ID', '<qr_code>')
            inline_image.add_header('Content-Disposition', 'inline', filename=f"{self.ticket_code}-qr.png")
            email.attach(inline_image)

            # Also a plain attachment, so it's unambiguously downloadable
            # as its own file even in clients that don't render inline images.
            email.attach(f"{self.ticket_code}-qr.png", qr_bytes, 'image/png')

        email.send(fail_silently=True)

    @property
    def is_paid(self):
        return self.status == self.STATUS_PAID
