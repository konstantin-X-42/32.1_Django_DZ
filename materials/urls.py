from django.urls import path
from rest_framework.routers import DefaultRouter
from materials.apps import MaterialsConfig
from materials.views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
)

# 30.1 задаем пространство имен приложения согласно стандартам Django
app_name = MaterialsConfig.name

# 30.1 инициализируем стандартный роутер DRF для автоматической генерации маршрутов ViewSet
router = DefaultRouter()
# 30.1 регистрируем эндпоинты для CRUD-операций с курсами по префиксу courses
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
    # 30.1 маршрут для создания нового урока (POST)
    path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    # 30.1 маршрут для получения списка всех уроков (GET)
    path('lessons/', LessonListAPIView.as_view(), name='lesson-list'),
    # 30.1 маршрут для получения детальной информации об уроке по его ID (GET)
    path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-get'),
    # 30.1 маршрут для редактирования урока по его ID (PUT, PATCH)
    path('lessons/update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    # 30.1 маршрут для удаления урока по его ID (DELETE)
    path('lessons/delete/<int:pk>/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
] + router.urls
