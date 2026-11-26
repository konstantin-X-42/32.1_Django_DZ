# 32.1 импортируем get_object_or_404, APIView и Response для реализации управления подпиской
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
# 31 импортируем стандартный класс проверки авторизации
from rest_framework.permissions import IsAuthenticated
# 32.1 добавляем импорт модели Subscription для работы с подписками на курсы
from materials.models import Course, Lesson, Subscription
from materials.serializers import CourseSerializer, LessonSerializer
# 31 импортируем классы разрешений для модераторов и владельцев объектов
from users.permissions import IsModer, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    # 30.1 указываем сериализатор для преобразования данных модели курса
    serializer_class = CourseSerializer
    # 30.1 определяем базовый набор объектов курсов из базы данных
    queryset = Course.objects.all()

    def perform_create(self, serializer):
        # 31 автоматически привязываем текущего пользователя в качестве владельца при создании курса
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        # 31 возвращаем все курсы модераторам и только собственные курсы обычным пользователям
        if self.request.user.groups.filter(name='moders').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def get_permissions(self):
        # 31 запрещаем модераторам создание курсов через логическое отрицание ~IsModer
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModer]
        # 31 разрешаем удаление курса только его владельцу (и не модератору)
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, ~IsModer, IsOwner]
        # 31 разрешаем просмотр и редактирование курса модераторам или его владельцу
        elif self.action in ('retrieve', 'update', 'partial_update'):
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
        # 31 разрешаем получение списка курсов всем авторизованным (фильтрация происходит в get_queryset)
        elif self.action == 'list':
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    # 30.1 указываем сериализатор для валидации и создания нового урока
    serializer_class = LessonSerializer
    # 31 запрещаем модераторам создавать новые уроки
    permission_classes = [IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        # 31 автоматически привязываем текущего пользователя в качестве владельца при создании урока
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    # 30.1 указываем сериализатор для отображения списка уроков
    serializer_class = LessonSerializer
    # 30.1 определяем базовый набор объектов уроков
    queryset = Lesson.objects.all()
    # 31 разрешаем просмотр списка уроков авторизованным пользователям
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 31 возвращаем все уроки модераторам и только собственные уроки обычным пользователям
        if self.request.user.groups.filter(name='moders').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    # 30.1 указываем сериализатор для детального просмотра одного урока
    serializer_class = LessonSerializer
    # 30.1 определяем набор объектов уроков для поиска по идентификатору
    queryset = Lesson.objects.all()
    # 31 разрешаем просмотр одного урока модератору или его владельцу
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    # 30.1 указываем сериализатор для полного или частичного обновления урока
    serializer_class = LessonSerializer
    # 30.1 определяем набор объектов уроков для поиска редактируемой записи
    queryset = Lesson.objects.all()
    # 31 разрешаем редактирование урока модератору или его владельцу
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    # 30.1 определяем набор объектов уроков для поиска и удаления записи
    queryset = Lesson.objects.all()
    # 31 разрешаем удаление урока только его владельцу (и не модератору)
    permission_classes = [IsAuthenticated, ~IsModer, IsOwner]


# 32.1 контроллер для установки или удаления подписки текущего пользователя на обновления курса
class SubscriptionAPIView(APIView):
    # 32.1 ограничиваем доступ к управлению подпиской только для авторизованных пользователей
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 32.1 получаем текущего авторизованного пользователя из запроса
        user = request.user
        # 32.1 извлекаем идентификатор курса из тела POST-запроса
        course_id = request.data.get('course_id')
        # 32.1 получаем объект курса из базы данных или возвращаем ошибку 404, если курс не найден
        course_item = get_object_or_404(Course, id=course_id)

        # 32.1 ищем существующую подписку текущего пользователя на выбранный курс
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            # 32.1 если подписка уже существует — удаляем её и формируем соответствующее сообщение
            subs_item.delete()
            message = 'подписка удалена'
        else:
            # 32.1 если подписки нет — создаем новую запись и формируем сообщение о добавлении
            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        # 32.1 возвращаем ответ API с результатом операции
        return Response({'message': message})


#----31---



# from rest_framework import viewsets, generics
# # 31 импортируем стандартный класс проверки авторизации
# from rest_framework.permissions import IsAuthenticated
# from materials.models import Course, Lesson
# from materials.serializers import CourseSerializer, LessonSerializer
# # 31 импортируем классы разрешений для модераторов и владельцев объектов
# from users.permissions import IsModer, IsOwner
#
#
# class CourseViewSet(viewsets.ModelViewSet):
#     # 30.1 указываем сериализатор для преобразования данных модели курса
#     serializer_class = CourseSerializer
#     # 30.1 определяем базовый набор объектов курсов из базы данных
#     queryset = Course.objects.all()
#
#     def perform_create(self, serializer):
#         # 31 автоматически привязываем текущего пользователя в качестве владельца при создании курса
#         serializer.save(owner=self.request.user)
#
#     def get_queryset(self):
#         # 31 возвращаем все курсы модераторам и только собственные курсы обычным пользователям
#         if self.request.user.groups.filter(name='moders').exists():
#             return Course.objects.all()
#         return Course.objects.filter(owner=self.request.user)
#
#     def get_permissions(self):
#         # 31 запрещаем модераторам создание курсов через логическое отрицание ~IsModer
#         if self.action == 'create':
#             self.permission_classes = [IsAuthenticated, ~IsModer]
#         # 31 разрешаем удаление курса только его владельцу (и не модератору)
#         elif self.action == 'destroy':
#             self.permission_classes = [IsAuthenticated, ~IsModer, IsOwner]
#         # 31 разрешаем просмотр и редактирование курса модераторам или его владельцу
#         elif self.action in ('retrieve', 'update', 'partial_update'):
#             self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
#         # 31 разрешаем получение списка курсов всем авторизованным (фильтрация происходит в get_queryset)
#         elif self.action == 'list':
#             self.permission_classes = [IsAuthenticated]
#         return [permission() for permission in self.permission_classes]
#
#
# class LessonCreateAPIView(generics.CreateAPIView):
#     # 30.1 указываем сериализатор для валидации и создания нового урока
#     serializer_class = LessonSerializer
#     # 31 запрещаем модераторам создавать новые уроки
#     permission_classes = [IsAuthenticated, ~IsModer]
#
#     def perform_create(self, serializer):
#         # 31 автоматически привязываем текущего пользователя в качестве владельца при создании урока
#         serializer.save(owner=self.request.user)
#
#
# class LessonListAPIView(generics.ListAPIView):
#     # 30.1 указываем сериализатор для отображения списка уроков
#     serializer_class = LessonSerializer
#     # 30.1 определяем базовый набор объектов уроков
#     queryset = Lesson.objects.all()
#     # 31 разрешаем просмотр списка уроков авторизованным пользователям
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         # 31 возвращаем все уроки модераторам и только собственные уроки обычным пользователям
#         if self.request.user.groups.filter(name='moders').exists():
#             return Lesson.objects.all()
#         return Lesson.objects.filter(owner=self.request.user)
#
#
# class LessonRetrieveAPIView(generics.RetrieveAPIView):
#     # 30.1 указываем сериализатор для детального просмотра одного урока
#     serializer_class = LessonSerializer
#     # 30.1 определяем набор объектов уроков для поиска по идентификатору
#     queryset = Lesson.objects.all()
#     # 31 разрешаем просмотр одного урока модератору или его владельцу
#     permission_classes = [IsAuthenticated, IsModer | IsOwner]
#
#
# class LessonUpdateAPIView(generics.UpdateAPIView):
#     # 30.1 указываем сериализатор для полного или частичного обновления урока
#     serializer_class = LessonSerializer
#     # 30.1 определяем набор объектов уроков для поиска редактируемой записи
#     queryset = Lesson.objects.all()
#     # 31 разрешаем редактирование урока модератору или его владельцу
#     permission_classes = [IsAuthenticated, IsModer | IsOwner]
#
#
# class LessonDestroyAPIView(generics.DestroyAPIView):
#     # 30.1 определяем набор объектов уроков для поиска и удаления записи
#     queryset = Lesson.objects.all()
#     # 31 разрешаем удаление урока только его владельцу (и не модератору)
#     permission_classes = [IsAuthenticated, ~IsModer, IsOwner]
