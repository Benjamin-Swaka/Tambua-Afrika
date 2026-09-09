from django.contrib import admin
from .models import Intent, ChatLog


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    list_display = ("name", "priority", "is_active", "trigger_preview", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "trigger_phrases", "response")
    list_editable = ("priority", "is_active")
    fieldsets = (
        (None, {"fields": ("name", "is_active", "priority")}),
        (
            "Matching",
            {
                "fields": ("trigger_phrases",),
                "description": (
                    "One phrase per line. The bot matches if a visitor's message "
                    "contains any of these (not case sensitive)."
                ),
            },
        ),
        ("Reply", {"fields": ("response",)}),
    )

    @admin.display(description="Triggers")
    def trigger_preview(self, obj):
        triggers = obj.trigger_list()
        preview = ", ".join(triggers[:3])
        if len(triggers) > 3:
            preview += f" (+{len(triggers) - 3} more)"
        return preview or "—"


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "message_preview", "matched_intent")
    list_filter = ("matched_intent",)
    search_fields = ("message", "reply_sent")
    readonly_fields = ("message", "matched_intent", "reply_sent", "session_key", "created_at")

    def has_add_permission(self, request):
        return False

    @admin.display(description="Message")
    def message_preview(self, obj):
        return obj.message[:80]
