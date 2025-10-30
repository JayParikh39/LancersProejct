from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('injuries/', include('injuries.urls')),
    path('tracking/', include('injury_tracking.urls', namespace='tracking')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
]
