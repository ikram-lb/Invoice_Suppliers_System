from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/accounts/', permanent=False)),  # Redirect root to accounts
    path('accounts/', include('accounts.urls')),
    path('', include('fact_app.urls')),  
]
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# Add static file handling for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
