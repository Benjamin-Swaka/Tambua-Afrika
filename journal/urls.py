from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='journal_home'),
    path('<slug:slug>/', views.detail, name='article_detail'),
]