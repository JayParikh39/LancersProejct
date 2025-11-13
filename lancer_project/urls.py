from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('injuries/', include('injuries.urls')),
    path('tracking/', include('injury_tracking.urls', namespace='tracking')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
]

# Serve static files in development
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
