from django.db import models


class Intent(models.Model):
    """
    A single manually-defined answer the chatbot can give.

    No ML training involved: an admin writes the phrases people might
    type (triggers) and the reply the bot should give (response).
    Matching is a simple, transparent keyword/substring match done in
    views.chatbot_reply — easy to reason about and easy for a
    non-technical admin to maintain.
    """

    name = models.CharField(
        max_length=120,
        help_text="Internal label, e.g. 'Opening hours' or 'Submission process'.",
    )
    trigger_phrases = models.TextField(
        help_text=(
            "One phrase or keyword per line. If a visitor's message contains "
            "any of these (case-insensitive), this intent can match. "
            "Example:\nopening hours\nwhat time are you open\nwhen open"
        )
    )
    response = models.TextField(
        help_text="The reply shown to the visitor. Plain text or simple HTML (e.g. <br>, <a>)."
    )
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Higher priority intents are checked first when several match the same message.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "name"]
        verbose_name = "Chatbot intent"
        verbose_name_plural = "Chatbot intents"

    def __str__(self):
        return self.name

    def trigger_list(self):
        return [
            line.strip().lower()
            for line in self.trigger_phrases.splitlines()
            if line.strip()
        ]


class ChatLog(models.Model):
    """
    Lightweight record of what visitors asked, and whether an Intent
    matched. Lets an admin see real questions and add new Intents for
    the ones the bot couldn't answer — without any training data.
    """

    message = models.TextField()
    matched_intent = models.ForeignKey(
        Intent, null=True, blank=True, on_delete=models.SET_NULL, related_name="logs"
    )
    reply_sent = models.TextField()
    session_key = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Chat log entry"
        verbose_name_plural = "Chat log entries"

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} — {self.message[:50]}"
