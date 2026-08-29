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
        self.status = self.STATUS_PAID
        self.paid_at = timezone.now()
        if reference:
            self.payment_reference = reference
        self.save()

    @property
    def is_paid(self):
        return self.status == self.STATUS_PAID
