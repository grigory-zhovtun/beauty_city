from django.contrib import admin
from django.urls import path, include, re_path # <-- Добавь include, re_path
from django.conf import settings
from django.conf.urls.static import static
from bot.webhook import webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^webhook/?, webhook),
    # Новая строка: все адреса из salon.urls будут доступны по префиксу /api/v1/
    path('api/v1/', include('salon.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)