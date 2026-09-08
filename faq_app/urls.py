from django.urls import path
from . import views

urlpatterns = [
    # Public
    path("", views.faq_list, name="faq_list"),

    # Staff dashboard management
    path("manage/", views.admin_faq_list, name="admin_list"),
    path("manage/add/", views.faq_add, name="faq_add"),
    path("manage/<int:pk>/edit/", views.faq_edit, name="faq_edit"),
    path("manage/<int:pk>/delete/", views.faq_delete, name="faq_delete"),
]