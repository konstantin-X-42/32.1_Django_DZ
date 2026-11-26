from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 30.1 подключаем маршруты приложения materials
    path('', include('materials.urls', namespace='materials')),
    # 30.1 подключаем маршруты приложения users для редактирования профиля
    path('', include('users.urls', namespace='users')),
]

# 30.1 добавляем маршруты для раздачи загруженных медиафайлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
