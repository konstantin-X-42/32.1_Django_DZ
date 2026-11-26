from django.urls import path
# 31 импортируем стандартные контроллеры SimpleJWT для получения и обновления пары токенов
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# 31 импортируем AllowAny для открытия эндпоинтов авторизации неавторизованным пользователям
from rest_framework.permissions import AllowAny
from users.apps import UsersConfig
# 31 импортируем контроллеры регистрации, списка и удаления пользователей вместе с существующими
from users.views import (
    UserCreateAPIView,
    UserListAPIView,
    UserUpdateAPIView,
    UserDestroyAPIView,
    PaymentListAPIView,
)

# 30.1 задаем пространство имен приложения users
app_name = UsersConfig.name

urlpatterns = [
    # 31 эндпоинт получения пары access и refresh JWT-токенов (открыт для всех)
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    # 31 эндпоинт обновления access-токена по refresh-токену (открыт для всех)
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='token-refresh'),

    # 31 маршрут регистрации нового пользователя (POST, открыт для всех)
    path('register/', UserCreateAPIView.as_view(), name='register'),
    # 31 маршрут получения списка всех пользователей (GET)
    path('users/', UserListAPIView.as_view(), name='user-list'),
    # 30.1 маршрут для получения и редактирования профиля любого пользователя по ID (GET, PUT, PATCH)
    path('users/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),
    # 31 маршрут для удаления пользователя по ID (DELETE)
    path('users/delete/<int:pk>/', UserDestroyAPIView.as_view(), name='user-delete'),

    # 30.2 маршрут для получения списка платежей с поддержкой фильтрации и сортировки (GET)
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
]


#---------30.2-------



# from django.urls import path
# from users.apps import UsersConfig
# # 30.2 импортируем контроллер списка платежей PaymentListAPIView
# from users.views import UserUpdateAPIView, PaymentListAPIView
#
# # 30.1 задаем пространство имен приложения users
# app_name = UsersConfig.name
#
# urlpatterns = [
#     # 30.1 маршрут для получения и редактирования профиля любого пользователя по ID (GET, PUT, PATCH)
#     path('users/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),
#     # 30.2 маршрут для получения списка платежей с поддержкой фильтрации и сортировки (GET)
#     path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
# ]
