from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='submission_dashboard'),
    path('new/', views.create_submission, name='new_submission'),
]