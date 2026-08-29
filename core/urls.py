from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('team/', views.team, name='team'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy'),
    path('terms-of-service/', views.terms_conditions, name='terms'),
    path('copyright-policy/', views.copyright_policy, name='copyright'),
    path('terms/', views.terms_conditions, name='terms'),
    path('newsletter/subscribe/', views.subscribe_newsletter, name='newsletter_subscribe'),
    path('search/', views.global_search, name='global_search'),
    path('select-department/', views.select_department, name='select_department'),
    path('cookies/', views.cookie_settings, name='cookie_settings'),

    # Campaigns
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/new/', views.campaign_create, name='campaign_create'),
    path('campaigns/dashboard/', views.campaign_dashboard, name='campaign_dashboard'),
    path(
        'campaigns/pledge/confirm/',
        views.campaign_pledge_confirm,
        name='campaign_pledge_confirm'
    ),
    path(
        'campaigns/<slug:slug>/edit/',
        views.campaign_edit,
        name='campaign_edit'
    ),
    path(
        'campaigns/<slug:slug>/pledge/',
        views.campaign_pledge,
        name='campaign_pledge'
    ),
    path(
        'campaigns/<slug:slug>/',
        views.campaign_detail,
        name='campaign_detail'
    ),
]