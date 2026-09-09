from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    # Public — called by the floating widget on the main site
    path("message/", views.chatbot_reply, name="message"),

    # Staff dashboard — manage intents without leaving the site
    path("admin/intents/", views.intent_list, name="admin_list"),
    path("admin/intents/new/", views.intent_create, name="admin_create"),
    path("admin/intents/<int:pk>/edit/", views.intent_edit, name="admin_edit"),
    path("admin/intents/<int:pk>/delete/", views.intent_delete, name="admin_delete"),
    path("admin/intents/<int:pk>/toggle/", views.intent_toggle, name="admin_toggle"),
    path("admin/logs/", views.chat_logs, name="admin_logs"),
]
