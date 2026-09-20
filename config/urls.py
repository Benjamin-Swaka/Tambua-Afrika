import re

from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.static import serve as serve_media
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
    path("chatbot/", include("chatbot.urls", namespace="chatbot")),
    
]

# Media (user-uploaded show posters, submission files/images, QR codes, etc.)
# must be served regardless of DEBUG -- this project has no S3/CDN configured,
# so without this every /media/... URL 404s in production (DEBUG=False), which
# is what was breaking show/ticket poster images and submission downloads.
#
# NOTE: django.conf.urls.static.static() -- used below for STATIC_URL -- is
# hard-coded to return an empty list unless settings.DEBUG is True, so it
# can't be reused for this even by dropping the "if settings.DEBUG:" guard
# around it. Media is wired directly to django.views.static.serve instead,
# via a pattern built from MEDIA_URL so it keeps working if that ever changes.
# This is the same file-serving view Django uses in development; for a
# high-traffic deployment, serving media from a dedicated storage backend
# (e.g. S3 + CloudFront) fronted by a CDN would be more scalable, but this
# fixes the site's broken images/downloads without adding new dependencies.
urlpatterns += [
    re_path(
        r'^' + re.escape(settings.MEDIA_URL.lstrip('/')) + r'(?P<path>.*)$',
        serve_media,
        {'document_root': settings.MEDIA_ROOT},
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)