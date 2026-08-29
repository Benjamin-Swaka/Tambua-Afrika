from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='comics_home'),
    path('<int:pk>/', views.detail, name='comic_detail'),
]