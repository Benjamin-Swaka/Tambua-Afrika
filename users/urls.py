from django.urls import path
from . import views

urlpatterns = [
    path('routing/', views.dashboard_routing, name='dashboard_routing'),
    path('overview/', views.user_dashboard, name='user_dashboard'),
    path('admin-panel/', views.staff_dashboard, name='staff_dashboard'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('privacy/', views.privacy_center, name='privacy_center'),
    path('privacy/export/', views.export_my_data, name='export_my_data'),
    path('privacy/delete/', views.delete_my_account, name='delete_my_account'),

    # Custom admin dashboard (staff-only)
    path('admin-panel/submissions/', views.admin_submissions, name='admin_submissions'),
    path('admin-panel/submissions/<int:pk>/status/', views.admin_submission_update_status, name='admin_submission_update_status'),
    path('admin-panel/tickets/', views.admin_tickets, name='admin_tickets'),
    path('admin-panel/tickets/<str:ticket_code>/status/', views.admin_ticket_update_status, name='admin_ticket_update_status'),
    path('admin-panel/manual-payments/', views.admin_manual_payments, name='admin_manual_payments'),
    path('admin-panel/manual-payments/<str:payment_reference>/', views.admin_manual_payment_review, name='admin_manual_payment_review'),
    path('admin-panel/shop/', views.admin_products, name='admin_products'),
    path('admin-panel/shop/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:pk>/toggle-staff/', views.admin_user_toggle_staff, name='admin_user_toggle_staff'),
    path('admin-panel/users/<int:pk>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),

    # Shows
    path('admin-panel/shows/', views.admin_shows, name='admin_shows'),
    path('admin-panel/shows/new/', views.admin_show_create, name='admin_show_create'),
    path('admin-panel/shows/<int:pk>/edit/', views.admin_show_edit, name='admin_show_edit'),
    path('admin-panel/shows/<int:pk>/delete/', views.admin_show_delete, name='admin_show_delete'),
    path('admin-panel/shows/<int:pk>/toggle-active/', views.admin_show_toggle_active, name='admin_show_toggle_active'),

    # Homepage content
    path('admin-panel/homepage/', views.admin_homepage_content, name='admin_homepage_content'),
    path('admin-panel/homepage/featured-works/new/', views.admin_featured_work_form, name='admin_featured_work_create'),
    path('admin-panel/homepage/featured-works/<int:pk>/edit/', views.admin_featured_work_form, name='admin_featured_work_edit'),
    path('admin-panel/homepage/featured-works/<int:pk>/delete/', views.admin_featured_work_delete, name='admin_featured_work_delete'),
    path('admin-panel/homepage/open-calls/new/', views.admin_open_call_form, name='admin_open_call_create'),
    path('admin-panel/homepage/open-calls/<int:pk>/edit/', views.admin_open_call_form, name='admin_open_call_edit'),
    path('admin-panel/homepage/open-calls/<int:pk>/delete/', views.admin_open_call_delete, name='admin_open_call_delete'),
    path('admin-panel/homepage/shop-highlights/new/', views.admin_shop_highlight_form, name='admin_shop_highlight_create'),
    path('admin-panel/homepage/shop-highlights/<int:pk>/edit/', views.admin_shop_highlight_form, name='admin_shop_highlight_edit'),
    path('admin-panel/homepage/shop-highlights/<int:pk>/delete/', views.admin_shop_highlight_delete, name='admin_shop_highlight_delete'),

    # Ticket door verification / check-in
    path('admin-panel/tickets/verify/', views.admin_ticket_verify, name='admin_ticket_verify'),
    path('admin-panel/tickets/verify/<str:ticket_code>/', views.admin_ticket_verify, name='admin_ticket_verify_code'),
]