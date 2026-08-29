from django.urls import path
from . import views

urlpatterns = [
    path('routing/', views.dashboard_routing, name='dashboard_routing'),
    path('overview/', views.user_dashboard, name='user_dashboard'),
    path('admin-panel/', views.staff_dashboard, name='staff_dashboard'),
    path('settings/', views.profile_settings, name='profile_settings'),
]