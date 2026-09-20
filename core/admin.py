from django.contrib import admin
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from .models import NewsletterSubscriber
from django.contrib import admin
from .models import ContactMessage
from django.contrib import admin
from .models import HomeDepartment

from .models import (
    Department, UserProfile, DepartmentMembership, EmailOTP, ConsentLog,
    FeaturedWork, OpenCall, ShopHighlight,
)

admin.site.register(Department)
admin.site.register(UserProfile)
admin.site.register(DepartmentMembership)
admin.site.register(EmailOTP)
admin.site.register(FeaturedWork)
admin.site.register(OpenCall)
admin.site.register(ShopHighlight)


@admin.register(ConsentLog)
class ConsentLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'analytics', 'marketing', 'ip_address', 'created_at')
    list_filter = ('analytics', 'marketing', 'created_at')
    search_fields = ('user__email', 'session_key', 'ip_address')
    readonly_fields = [f.name for f in ConsentLog._meta.fields]

    def has_add_permission(self, request):
        # Consent records are written by the app, not created manually.
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'consent_display',
        'is_active',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'consent',         # filter by consent (True/False)
        'is_active',
        'created_at',
    )
    search_fields = ('email',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def consent_display(self, obj):
        """Show a coloured Yes/No instead of True/False."""
        if obj.consent:
            return mark_safe('<span style="color: #2e7d32; font-weight: bold;">✓ Yes</span>')
        return mark_safe('<span style="color: #c62828; font-weight: bold;">✗ No</span>')
    consent_display.short_description = 'Consent Given'




@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('subject', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_editable = ('is_read',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'ip_address', 'created_at')

    fieldsets = (
        ('Sender', {'fields': ('name', 'email', 'subject')}),
        ('Message', {'fields': ('message',)}),
        ('Status', {'fields': ('is_read',)}),
        ('Metadata', {'fields': ('ip_address', 'created_at'), 'classes': ('collapse',)}),
    )

    def has_add_permission(self, request):
        # Messages should only ever be created via the public contact form.
        return False



@admin.register(HomeDepartment)
class HomeDepartmentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'label', 'accent', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter   = ('accent', 'icon', 'is_active')
    search_fields = ('name', 'label', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'label', 'description')
        }),
        ('Appearance', {
            'fields': ('accent', 'icon')
        }),
        ('Link', {
            'fields': ('link_url', 'link_text')
        }),
        ('Visibility', {
            'fields': ('order', 'is_active')
        }),
    )