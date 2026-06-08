from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from home.views import custom_login
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Serve favicon.ico — Google checks this path for search result favicons
    path('favicon.ico', RedirectView.as_view(url='/static/images/fav-icon.png', permanent=True)),
    path('', include('home.urls')),
    path('about/', include('about.urls')),
    path('services/', include('services.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('pricing/', include('pricing.urls')),
    path('contact/', include('contact.urls')),
    path('request-website/', include('requestsite.urls')),
    path('accounts/login/', custom_login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('panel/', include('adminpanel.urls')),
    path('panel/agreements/', include('agreement.urls')),
    path('panel/projects/', include('dashboard.urls')),
    path('features/', include('features.urls')),
    path('notifications/', include('notifications.urls')),
    path('agent/', include('agent.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
