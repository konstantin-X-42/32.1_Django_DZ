from rest_framework import generics
# 31 импортируем разрешения AllowAny и IsAuthenticated для настройки прав доступа
from rest_framework.permissions import AllowAny, IsAuthenticated
# 30.2 импортируем бэкенды для фильтрации по полям и сортировки результатов
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
# 30.2 импортируем модель Payment и сериализатор PaymentSerializer
from users.models import User, Payment
# 31 добавляем импорт UserRegisterSerializer и UserPublicSerializer
from users.serializers import UserSerializer, UserPublicSerializer, UserRegisterSerializer, PaymentSerializer
# 31 импортируем класс прав доступа для проверки владельца профиля
from users.permissions import IsCurrentUser


# 31 контроллер для регистрации нового пользователя (открыт для неавторизованных пользователей)
class UserCreateAPIView(generics.CreateAPIView):
    # 31 указываем сериализатор регистрации с проверкой уникальности email и хешированием пароля
    serializer_class = UserRegisterSerializer
    # 31 передаем набор всех пользователей
    queryset = User.objects.all()
    # 31 разрешаем доступ к регистрации всем пользователям без токена
    permission_classes = (AllowAny,)


# 31 контроллер для получения списка всех зарегистрированных пользователей
class UserListAPIView(generics.ListAPIView):
    # 31 используем публичный сериализатор, чтобы скрыть фамилии и платежи других пользователей в общем списке
    serializer_class = UserPublicSerializer
    # 31 передаем набор всех пользователей из базы данных
    queryset = User.objects.all()


class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
    # 30.1 передаем набор всех пользователей для просмотра или редактирования профиля по ID
    queryset = User.objects.all()

    def get_serializer_class(self):
        # 31 возвращаем полный сериализатор для своего профиля и сокращенный публичный для чужого
        if self.kwargs.get('pk') == self.request.user.pk:
            return UserSerializer
        return UserPublicSerializer

    def get_permissions(self):
        # 31 разрешаем просмотр (GET) любого профиля всем авторизованным пользователям
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        # 31 разрешаем редактирование (PUT, PATCH) только владельцу профиля
        else:
            self.permission_classes = [IsAuthenticated, IsCurrentUser]
        return [permission() for permission in self.permission_classes]


# 31 контроллер для удаления учетной записи пользователя по ID
class UserDestroyAPIView(generics.DestroyAPIView):
    # 31 передаем набор всех пользователей для поиска и удаления записи
    queryset = User.objects.all()
    # 31 разрешаем удалять профиль только его владельцу
    permission_classes = [IsAuthenticated, IsCurrentUser]


class PaymentListAPIView(generics.ListAPIView):
    # 30.2 указываем сериализатор для отображения списка платежей
    serializer_class = PaymentSerializer
    # 30.2 передаем набор всех платежей из базы данных
    queryset = Payment.objects.all()
    # 30.2 подключаем бэкенды фильтрации и сортировки для данного эндпоинта
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # 30.2 разрешаем фильтрацию по оплаченному курсу, уроку и способу оплаты
    filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')
    # 30.2 разрешаем сортировку по дате оплаты (по возрастанию и убыванию)
    ordering_fields = ('payment_date',)



# ----до доп---


# from rest_framework import generics
# # 31 импортируем разрешение AllowAny для открытия эндпоинта регистрации неавторизованным пользователям
# from rest_framework.permissions import AllowAny
# # 30.2 импортируем бэкенды для фильтрации по полям и сортировки результатов
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import OrderingFilter
# # 30.2 импортируем модель Payment и сериализатор PaymentSerializer
# from users.models import User, Payment
# # 31 добавляем импорт UserRegisterSerializer для регистрации новых пользователей
# from users.serializers import UserSerializer, UserRegisterSerializer, PaymentSerializer
#
#
# # 31 контроллер для регистрации нового пользователя (открыт для неавторизованных пользователей)
# class UserCreateAPIView(generics.CreateAPIView):
#     # 31 указываем сериализатор регистрации с проверкой уникальности email и хешированием пароля
#     serializer_class = UserRegisterSerializer
#     # 31 передаем набор всех пользователей
#     queryset = User.objects.all()
#     # 31 разрешаем доступ к регистрации всем пользователям без токена
#     permission_classes = (AllowAny,)
#
#
# # 31 контроллер для получения списка всех зарегистрированных пользователей
# class UserListAPIView(generics.ListAPIView):
#     # 31 указываем сериализатор для отображения списка пользователей
#     serializer_class = UserSerializer
#     # 31 передаем набор всех пользователей из базы данных
#     queryset = User.objects.all()
#
#
# class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
#     # 30.1 указываем сериализатор для просмотра и обновления профиля пользователя
#     serializer_class = UserSerializer
#     # 30.1 передаем набор всех пользователей для возможности редактирования любого профиля по ID
#     queryset = User.objects.all()
#
#
# # 31 контроллер для удаления учетной записи пользователя по ID
# class UserDestroyAPIView(generics.DestroyAPIView):
#     # 31 передаем набор всех пользователей для поиска и удаления записи
#     queryset = User.objects.all()
#
#
# class PaymentListAPIView(generics.ListAPIView):
#     # 30.2 указываем сериализатор для отображения списка платежей
#     serializer_class = PaymentSerializer
#     # 30.2 передаем набор всех платежей из базы данных
#     queryset = Payment.objects.all()
#     # 30.2 подключаем бэкенды фильтрации и сортировки для данного эндпоинта
#     filter_backends = [DjangoFilterBackend, OrderingFilter]
#     # 30.2 разрешаем фильтрацию по оплаченному курсу, уроку и способу оплаты
#     filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')
#     # 30.2 разрешаем сортировку по дате оплаты (по возрастанию и убыванию)
#     ordering_fields = ('payment_date',)



#-----30.2-----



# from rest_framework import generics
# # 30.2 импортируем бэкенды для фильтрации по полям и сортировки результатов
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import OrderingFilter
# # 30.2 импортируем модель Payment и сериализатор PaymentSerializer
# from users.models import User, Payment
# from users.serializers import UserSerializer, PaymentSerializer
#
#
# class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
#     # 30.1 указываем сериализатор для просмотра и обновления профиля пользователя
#     serializer_class = UserSerializer
#     # 30.1 передаем набор всех пользователей для возможности редактирования любого профиля по ID
#     queryset = User.objects.all()
#
#
# class PaymentListAPIView(generics.ListAPIView):
#     # 30.2 указываем сериализатор для отображения списка платежей
#     serializer_class = PaymentSerializer
#     # 30.2 передаем набор всех платежей из базы данных
#     queryset = Payment.objects.all()
#     # 30.2 подключаем бэкенды фильтрации и сортировки для данного эндпоинта
#     filter_backends = [DjangoFilterBackend, OrderingFilter]
#     # 30.2 разрешаем фильтрацию по оплаченному курсу, уроку и способу оплаты
#     filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')
#     # 30.2 разрешаем сортировку по дате оплаты (по возрастанию и убыванию)
#     ordering_fields = ('payment_date',)
