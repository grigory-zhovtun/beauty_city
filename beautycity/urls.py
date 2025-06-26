from django.contrib import admin
from django.urls import path, include # <-- Добавь include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Новая строка: все адреса из salon.urls будут доступны по префиксу /api/v1/
    path('api/v1/', include('salon.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)