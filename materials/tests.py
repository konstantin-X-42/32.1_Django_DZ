# 32.1 импортируем модель Group для создания группы модераторов в тестовой базе данных
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


# 32.1 набор тестов для проверки CRUD-операций с уроками и разграничения прав доступа
class LessonTestCase(APITestCase):

    def setUp(self):
        # 32.1 создаем группу модераторов moders для проверки их прав доступа
        self.moder_group = Group.objects.create(name='moders')

        # 32.1 создаем пользователя-владельца курса и урока
        self.owner = User.objects.create(email='owner@test.ru')
        # 32.1 создаем модератора и добавляем его в группу moders
        self.moder = User.objects.create(email='moder@test.ru')
        self.moder.groups.add(self.moder_group)
        # 32.1 создаем стороннего авторизованного пользователя без прав владельца и модератора
        self.other_user = User.objects.create(email='other@test.ru')

        # 32.1 создаем тестовый курс и урок, принадлежащие владельцу owner
        self.course = Course.objects.create(
            title='Тестовый курс',
            description='Описание тестового курса',
            owner=self.owner
        )
        self.lesson = Lesson.objects.create(
            title='Тестовый урок',
            description='Описание тестового урока',
            video_url='https://youtube.com',
            course=self.course,
            owner=self.owner
        )

    def test_lesson_create_by_user(self):
        # 32.1 авторизуем обычного пользователя и проверяем успешное создание урока со ссылкой на YouTube
        self.client.force_authenticate(user=self.owner)
        url = reverse('materials:lesson-create')
        data = {
            'title': 'Новый урок',
            'description': 'Описание нового урока',
            'video_url': 'https://youtube.com',
            'course': self.course.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.get(title='Новый урок').owner, self.owner)

    def test_lesson_create_invalid_url(self):
        # 32.1 проверяем отклонение создания урока при передаче ссылки не на youtube.com
        self.client.force_authenticate(user=self.owner)
        url = reverse('materials:lesson-create')
        data = {
            'title': 'Урок с плохой ссылкой',
            'video_url': 'https://rutube.ru',
            'course': self.course.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_create_forbidden_for_moder(self):
        # 32.1 проверяем запрет на создание урока для модератора (403 Forbidden)
        self.client.force_authenticate(user=self.moder)
        url = reverse('materials:lesson-create')
        data = {
            'title': 'Урок от модератора',
            'video_url': 'https://youtube.com',
            'course': self.course.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_list_and_pagination(self):
        # 32.1 проверяем получение списка уроков владельцем и наличие структуры пагинации
        self.client.force_authenticate(user=self.owner)
        url = reverse('materials:lesson-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

        # 32.1 проверяем, что посторонний пользователь не видит чужие уроки в списке
        self.client.force_authenticate(user=self.other_user)
        response_other = self.client.get(url)
        self.assertEqual(response_other.status_code, status.HTTP_200_OK)
        self.assertEqual(response_other.data['count'], 0)

        # 32.1 проверяем, что модератор видит все уроки в системе
        self.client.force_authenticate(user=self.moder)
        response_moder = self.client.get(url)
        self.assertEqual(response_moder.status_code, status.HTTP_200_OK)
        self.assertEqual(response_moder.data['count'], 1)

    def test_lesson_retrieve_permissions(self):
        # 32.1 проверяем просмотр деталей урока владельцем, модератором и запрет для чужого пользователя
        url = reverse('materials:lesson-get', args=(self.lesson.pk,))

        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.moder)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.other_user)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_permissions(self):
        # 32.1 проверяем редактирование урока владельцем и модератором, а также запрет для чужого пользователя
        url = reverse('materials:lesson-update', args=(self.lesson.pk,))

        self.client.force_authenticate(user=self.owner)
        response_owner = self.client.patch(url, {'title': 'Обновлено владельцем'})
        self.assertEqual(response_owner.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновлено владельцем')

        self.client.force_authenticate(user=self.moder)
        response_moder = self.client.patch(url, {'title': 'Обновлено модератором'})
        self.assertEqual(response_moder.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.other_user)
        response_other = self.client.patch(url, {'title': 'Попытка взлома'})
        self.assertEqual(response_other.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_forbidden_for_moder_and_other(self):
        # 32.1 проверяем запрет удаления урока для модератора и постороннего пользователя
        url = reverse('materials:lesson-delete', args=(self.lesson.pk,))

        self.client.force_authenticate(user=self.moder)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.other_user)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_delete_by_owner(self):
        # 32.1 проверяем успешное удаление урока его владельцем
        url = reverse('materials:lesson-delete', args=(self.lesson.pk,))
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)


# 32.1 набор тестов для проверки функционала подписки и отписки от обновлений курса
class SubscriptionTestCase(APITestCase):

    def setUp(self):
        # 32.1 создаем тестового пользователя и курс для проверки подписки
        self.user = User.objects.create(email='subscriber@test.ru')
        self.course = Course.objects.create(
            title='Курс для подписки',
            description='Описание курса',
            owner=self.user
        )
        self.subscribe_url = reverse('materials:course-subscribe')

    def test_subscription_toggle_and_course_flag(self):
        # 32.1 авторизуем пользователя и выполняем первый POST-запрос для оформления подписки
        self.client.force_authenticate(user=self.user)
        response_add = self.client.post(self.subscribe_url, {'course_id': self.course.pk})
        self.assertEqual(response_add.status_code, status.HTTP_200_OK)
        self.assertEqual(response_add.data['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # 32.1 проверяем, что в детальной информации о курсе поле is_subscribed равно True
        course_detail_url = reverse('materials:courses-detail', args=(self.course.pk,))
        course_response = self.client.get(course_detail_url)
        self.assertEqual(course_response.status_code, status.HTTP_200_OK)
        self.assertTrue(course_response.data['is_subscribed'])

        # 32.1 выполняем повторный POST-запрос для удаления существующей подписки
        response_remove = self.client.post(self.subscribe_url, {'course_id': self.course.pk})
        self.assertEqual(response_remove.status_code, status.HTTP_200_OK)
        self.assertEqual(response_remove.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_unauthorized(self):
        # 32.1 проверяем, что неавторизованный пользователь не может управлять подпиской
        response = self.client.post(self.subscribe_url, {'course_id': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# 32.1 набор тестов для проверки CRUD-операций с курсами и разграничения прав доступа
class CourseTestCase(APITestCase):

    def setUp(self):
        # 32.1 создаем группу модераторов moders для проверки их прав доступа к курсам
        self.moder_group = Group.objects.create(name='moders')

        # 32.1 создаем владельца курса, модератора и стороннего пользователя
        self.owner = User.objects.create(email='course_owner@test.ru')
        self.moder = User.objects.create(email='course_moder@test.ru')
        self.moder.groups.add(self.moder_group)
        self.other_user = User.objects.create(email='course_other@test.ru')



#--32.1 до доп


# # 32.1 импортируем модель Group для создания группы модераторов в тестовой базе данных
# from django.contrib.auth.models import Group
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
#
# from materials.models import Course, Lesson, Subscription
# from users.models import User
#
#
# # 32.1 набор тестов для проверки CRUD-операций с уроками и разграничения прав доступа
# class LessonTestCase(APITestCase):
#
#     def setUp(self):
#         # 32.1 создаем группу модераторов moders для проверки их прав доступа
#         self.moder_group = Group.objects.create(name='moders')
#
#         # 32.1 создаем пользователя-владельца курса и урока
#         self.owner = User.objects.create(email='owner@test.ru')
#         # 32.1 создаем модератора и добавляем его в группу moders
#         self.moder = User.objects.create(email='moder@test.ru')
#         self.moder.groups.add(self.moder_group)
#         # 32.1 создаем стороннего авторизованного пользователя без прав владельца и модератора
#         self.other_user = User.objects.create(email='other@test.ru')
#
#         # 32.1 создаем тестовый курс и урок, принадлежащие владельцу owner
#         self.course = Course.objects.create(
#             title='Тестовый курс',
#             description='Описание тестового курса',
#             owner=self.owner
#         )
#         self.lesson = Lesson.objects.create(
#             title='Тестовый урок',
#             description='Описание тестового урока',
#             video_url='https://youtube.com',
#             course=self.course,
#             owner=self.owner
#         )
#
#     def test_lesson_create_by_user(self):
#         # 32.1 авторизуем обычного пользователя и проверяем успешное создание урока со ссылкой на YouTube
#         self.client.force_authenticate(user=self.owner)
#         url = reverse('materials:lesson-create')
#         data = {
#             'title': 'Новый урок',
#             'description': 'Описание нового урока',
#             'video_url': 'https://youtube.com',
#             'course': self.course.pk
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Lesson.objects.count(), 2)
#         self.assertEqual(Lesson.objects.get(title='Новый урок').owner, self.owner)
#
#     def test_lesson_create_invalid_url(self):
#         # 32.1 проверяем отклонение создания урока при передаче ссылки не на youtube.com
#         self.client.force_authenticate(user=self.owner)
#         url = reverse('materials:lesson-create')
#         data = {
#             'title': 'Урок с плохой ссылкой',
#             'video_url': 'https://rutube.ru',
#             'course': self.course.pk
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(Lesson.objects.count(), 1)
#
#     def test_lesson_create_forbidden_for_moder(self):
#         # 32.1 проверяем запрет на создание урока для модератора (403 Forbidden)
#         self.client.force_authenticate(user=self.moder)
#         url = reverse('materials:lesson-create')
#         data = {
#             'title': 'Урок от модератора',
#             'video_url': 'https://youtube.com',
#             'course': self.course.pk
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_lesson_list_and_pagination(self):
#         # 32.1 проверяем получение списка уроков владельцем и наличие структуры пагинации
#         self.client.force_authenticate(user=self.owner)
#         url = reverse('materials:lesson-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['count'], 1)
#         self.assertEqual(len(response.data['results']), 1)
#
#         # 32.1 проверяем, что посторонний пользователь не видит чужие уроки в списке
#         self.client.force_authenticate(user=self.other_user)
#         response_other = self.client.get(url)
#         self.assertEqual(response_other.status_code, status.HTTP_200_OK)
#         self.assertEqual(response_other.data['count'], 0)
#
#         # 32.1 проверяем, что модератор видит все уроки в системе
#         self.client.force_authenticate(user=self.moder)
#         response_moder = self.client.get(url)
#         self.assertEqual(response_moder.status_code, status.HTTP_200_OK)
#         self.assertEqual(response_moder.data['count'], 1)
#
#     def test_lesson_retrieve_permissions(self):
#         # 32.1 проверяем просмотр деталей урока владельцем, модератором и запрет для чужого пользователя
#         url = reverse('materials:lesson-get', args=(self.lesson.pk,))
#
#         self.client.force_authenticate(user=self.owner)
#         self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
#
#         self.client.force_authenticate(user=self.moder)
#         self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
#
#         self.client.force_authenticate(user=self.other_user)
#         self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_lesson_update_permissions(self):
#         # 32.1 проверяем редактирование урока владельцем и модератором, а также запрет для чужого пользователя
#         url = reverse('materials:lesson-update', args=(self.lesson.pk,))
#
#         self.client.force_authenticate(user=self.owner)
#         response_owner = self.client.patch(url, {'title': 'Обновлено владельцем'})
#         self.assertEqual(response_owner.status_code, status.HTTP_200_OK)
#         self.lesson.refresh_from_db()
#         self.assertEqual(self.lesson.title, 'Обновлено владельцем')
#
#         self.client.force_authenticate(user=self.moder)
#         response_moder = self.client.patch(url, {'title': 'Обновлено модератором'})
#         self.assertEqual(response_moder.status_code, status.HTTP_200_OK)
#
#         self.client.force_authenticate(user=self.other_user)
#         response_other = self.client.patch(url, {'title': 'Попытка взлома'})
#         self.assertEqual(response_other.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_lesson_delete_forbidden_for_moder_and_other(self):
#         # 32.1 проверяем запрет удаления урока для модератора и постороннего пользователя
#         url = reverse('materials:lesson-delete', args=(self.lesson.pk,))
#
#         self.client.force_authenticate(user=self.moder)
#         self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
#
#         self.client.force_authenticate(user=self.other_user)
#         self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(Lesson.objects.count(), 1)
#
#     def test_lesson_delete_by_owner(self):
#         # 32.1 проверяем успешное удаление урока его владельцем
#         url = reverse('materials:lesson-delete', args=(self.lesson.pk,))
#         self.client.force_authenticate(user=self.owner)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(Lesson.objects.count(), 0)
#
#
# # 32.1 набор тестов для проверки функционала подписки и отписки от обновлений курса
# class SubscriptionTestCase(APITestCase):
#
#     def setUp(self):
#         # 32.1 создаем тестового пользователя и курс для проверки подписки
#         self.user = User.objects.create(email='subscriber@test.ru')
#         self.course = Course.objects.create(
#             title='Курс для подписки',
#             description='Описание курса',
#             owner=self.user
#         )
#         self.subscribe_url = reverse('materials:course-subscribe')
#
#     def test_subscription_toggle_and_course_flag(self):
#         # 32.1 авторизуем пользователя и выполняем первый POST-запрос для оформления подписки
#         self.client.force_authenticate(user=self.user)
#         response_add = self.client.post(self.subscribe_url, {'course_id': self.course.pk})
#         self.assertEqual(response_add.status_code, status.HTTP_200_OK)
#         self.assertEqual(response_add.data['message'], 'подписка добавлена')
#         self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())
#
#         # 32.1 проверяем, что в детальной информации о курсе поле is_subscribed равно True
#         course_detail_url = reverse('materials:courses-detail', args=(self.course.pk,))
#         course_response = self.client.get(course_detail_url)
#         self.assertEqual(course_response.status_code, status.HTTP_200_OK)
#         self.assertTrue(course_response.data['is_subscribed'])
#
#         # 32.1 выполняем повторный POST-запрос для удаления существующей подписки
#         response_remove = self.client.post(self.subscribe_url, {'course_id': self.course.pk})
#         self.assertEqual(response_remove.status_code, status.HTTP_200_OK)
#         self.assertEqual(response_remove.data['message'], 'подписка удалена')
#         self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())
#
#     def test_subscription_unauthorized(self):
#         # 32.1 проверяем, что неавторизованный пользователь не может управлять подпиской
#         response = self.client.post(self.subscribe_url, {'course_id': self.course.pk})
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
