from django.contrib import admin

from .models import ManualPayment, Show, Ticket


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'venue', 'price', 'capacity',
                     'tickets_reserved', 'tickets_remaining', 'is_active')
    list_filter = ('is_active', 'date')
    search_fields = ('title', 'venue')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'show', 'user', 'quantity', 'total_amount',
                     'status', 'payment_reference', 'created_at', 'paid_at')
    list_filter = ('status', 'show')
    search_fields = ('ticket_code', 'user__email', 'user__username', 'payment_reference')
    readonly_fields = (
        'ticket_code',
        'total_amount',
        'status',
        'payment_reference',
        'pesapal_tracking_id',
        'qr_code',
        'checked_in',
        'checked_in_at',
        'checked_in_by',
        'created_at',
        'paid_at',
    )


@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_reference',
        'ticket',
        'amount',
        'paybill',
        'account_number',
        'transaction_code',
        'status',
        'submitted_at',
        'verified_at',
        'verified_by',
    )
    list_filter = ('status', 'paybill')
    search_fields = (
        'payment_reference',
        'transaction_code',
        'ticket__ticket_code',
        'ticket__user__email',
    )
    readonly_fields = (
        'payment_reference',
        'ticket',
        'amount',
        'paybill',
        'account_number',
        'transaction_code',
        'submitted_at',
        'verified_at',
        'verified_by',
        'created_at',
        'updated_at',
    )
