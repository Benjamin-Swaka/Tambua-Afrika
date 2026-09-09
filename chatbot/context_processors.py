from .models import ChatLog


def chatbot_stats(request):
    """
    Adds `unmatched_chatbot_count` to every template's context so the
    sidebar badge in dashboard_base.html stays accurate without every
    view needing to pass it explicitly.

    Register in settings.py:
        TEMPLATES = [{
            ...
            "OPTIONS": {
                "context_processors": [
                    ...
                    "chatbot.context_processors.chatbot_stats",
                ],
            },
        }]
    """
    if not (request.user.is_authenticated and request.user.is_staff):
        return {}
    return {"unmatched_chatbot_count": ChatLog.objects.filter(matched_intent__isnull=True).count()}
