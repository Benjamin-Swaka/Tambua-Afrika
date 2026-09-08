from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Department Apps
    path('', include('core.urls')),
    path('ink/', include('ink.urls')),
    path('stage/', include('stage.urls')),
    path('comics/', include('comics.urls')),
    path('shop/', include('shop.urls')),
    path('submissions/', include('submissions.urls')),
    path('journal/', include('journal.urls')),
    path('accounts/', include('allauth.urls')), 
    path('dashboard/', include('users.urls')),
    path('select-department/', core_views.select_department, name='select_department'),
    path("faq/", include("faq_app.urls")),
    path('i18n/', include('django.conf.urls.i18n')), 
    

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)