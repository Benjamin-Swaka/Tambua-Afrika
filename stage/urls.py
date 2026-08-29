from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='stage_home'),
    path('tickets/', views.my_tickets, name='my_tickets'),
    path('show/<slug:slug>/', views.show_detail, name='show_detail'),
    path('show/<slug:slug>/reserve/', views.reserve_ticket, name='reserve_ticket'),
    path('ticket/<str:ticket_code>/pay/', views.ticket_payment, name='ticket_payment'),
    path('ticket/<str:ticket_code>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<str:ticket_code>/cancel/', views.cancel_ticket, name='cancel_ticket'),
]
