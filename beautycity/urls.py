from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from bot.webhook import webhook   # ваша вьюха

urlpatterns = [
    path('admin/', admin.site.urls),

    # Webhook: допускаем необязательный завершающий «/»
    re_path(r'^webhook/?$', webhook),

    # Все роуты из salon доступны по префиксу /api/v1/
    path('api/v1/', include('salon.urls')),
]

# Раздаём MEDIA-файлы локально только в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)