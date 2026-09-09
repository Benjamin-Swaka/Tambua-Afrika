import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import IntentForm
from .models import ChatLog, Intent

FALLBACK_REPLY = (
    "I don't have an answer for that yet. You can reach our team directly on "
    "WhatsApp (the green button) or through the Contact page, and we'll get "
    "back to you personally."
)

MAX_MESSAGE_LENGTH = 500


# ---------------------------------------------------------------------------
# Public chat API — used by the floating widget on the main site
# ---------------------------------------------------------------------------

def _find_intent(message: str):
    """
    Plain substring matching against admin-defined trigger phrases.
    No ML, no training data — just an ordered scan over active Intents.
    """
    normalized = message.strip().lower()
    if not normalized:
        return None

    for intent in Intent.objects.filter(is_active=True).order_by("-priority", "name"):
        for trigger in intent.trigger_list():
            if trigger and trigger in normalized:
                return intent
    return None


@require_POST
def chatbot_reply(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request."}, status=400)

    message = str(payload.get("message", "")).strip()[:MAX_MESSAGE_LENGTH]

    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    intent = _find_intent(message)
    reply = intent.response if intent else FALLBACK_REPLY

    ChatLog.objects.create(
        message=message,
        matched_intent=intent,
        reply_sent=reply,
        session_key=request.session.session_key or "",
    )

    return JsonResponse(
        {
            "reply": reply,
            "matched": intent is not None,
        }
    )


# ---------------------------------------------------------------------------
# Staff dashboard views — manage intents without touching /admin/
# ---------------------------------------------------------------------------

def _is_staff(user):
    return user.is_authenticated and user.is_staff


staff_required = user_passes_test(_is_staff, login_url="account_login")


@login_required
@staff_required
def intent_list(request):
    intents = Intent.objects.all()
    recent_unmatched = (
        ChatLog.objects.filter(matched_intent__isnull=True).order_by("-created_at")[:8]
    )

    context = {
        "segment": "admin_chatbot",
        "intents": intents,
        "total_intents": intents.count(),
        "active_intents": intents.filter(is_active=True).count(),
        "inactive_intents": intents.filter(is_active=False).count(),
        "unmatched_count": ChatLog.objects.filter(matched_intent__isnull=True).count(),
        "recent_unmatched": recent_unmatched,
    }
    return render(request, "chatbot/admin/intent_list.html", context)


@login_required
@staff_required
def intent_create(request):
    seed = request.GET.get("seed", "").strip()
    initial = {"trigger_phrases": seed} if seed else {}

    if request.method == "POST":
        form = IntentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Intent created.")
            return redirect("chatbot:admin_list")
    else:
        form = IntentForm(initial=initial)

    context = {
        "segment": "admin_chatbot",
        "form": form,
        "is_new": True,
    }
    return render(request, "chatbot/admin/intent_form.html", context)


@login_required
@staff_required
def intent_edit(request, pk):
    intent = get_object_or_404(Intent, pk=pk)

    if request.method == "POST":
        form = IntentForm(request.POST, instance=intent)
        if form.is_valid():
            form.save()
            messages.success(request, "Intent updated.")
            return redirect("chatbot:admin_list")
    else:
        form = IntentForm(instance=intent)

    context = {
        "segment": "admin_chatbot",
        "form": form,
        "intent": intent,
        "is_new": False,
    }
    return render(request, "chatbot/admin/intent_form.html", context)


@login_required
@staff_required
def intent_delete(request, pk):
    intent = get_object_or_404(Intent, pk=pk)

    if request.method == "POST":
        intent.delete()
        messages.success(request, "Intent deleted.")
        return redirect("chatbot:admin_list")

    context = {
        "segment": "admin_chatbot",
        "intent": intent,
    }
    return render(request, "chatbot/admin/intent_confirm_delete.html", context)


@login_required
@staff_required
@require_POST
def intent_toggle(request, pk):
    intent = get_object_or_404(Intent, pk=pk)
    intent.is_active = not intent.is_active
    intent.save(update_fields=["is_active"])
    messages.success(
        request, f"“{intent.name}” is now {'active' if intent.is_active else 'inactive'}."
    )
    next_url = request.POST.get("next") or reverse("chatbot:admin_list")
    return redirect(next_url)


@login_required
@staff_required
def chat_logs(request):
    logs = ChatLog.objects.select_related("matched_intent").order_by("-created_at")

    show_unmatched_only = request.GET.get("filter") == "unmatched"
    if show_unmatched_only:
        logs = logs.filter(matched_intent__isnull=True)

    paginator = Paginator(logs, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "segment": "admin_chatbot",
        "page_obj": page_obj,
        "show_unmatched_only": show_unmatched_only,
        "unmatched_count": ChatLog.objects.filter(matched_intent__isnull=True).count(),
    }
    return render(request, "chatbot/admin/chat_logs.html", context)
