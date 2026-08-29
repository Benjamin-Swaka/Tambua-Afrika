from django.contrib import admin

from .models import Show, Ticket


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
    readonly_fields = ('ticket_code', 'total_amount', 'created_at', 'paid_at')
    actions = ['mark_selected_as_paid']

    @admin.action(description="Mark selected tickets as paid (manual confirmation)")
    def mark_selected_as_paid(self, request, queryset):
        updated = 0
        for ticket in queryset.exclude(status=Ticket.STATUS_PAID):
            ticket.mark_as_paid()
            updated += 1
        self.message_user(request, f"{updated} ticket(s) marked as paid.")
