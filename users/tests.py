from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# 32.1 импортируем модели Course, Lesson, User и Payment для подготовки тестовых данных
from materials.models import Course, Lesson
from users.models import User, Payment


# 32.1 набор тестов для проверки регистрации, получения и обновления JWT-токенов
class AuthTestCase(APITestCase):

    def setUp(self):
        # 32.1 создаем тестового пользователя с паролем для проверки входа по JWT
        self.user = User.objects.create(email='auth_user@test.ru')
        self.user.set_password('StrongPass123!')
        self.user.save()

    def test_user_register(self):
        # 32.1 проверяем регистрацию нового пользователя через эндпоинт POST /register/
        url = reverse('users:register')
        data = {
            'email': 'new_user@test.ru',
            'password': 'NewUserPass123!',
            'phone': '+79991234567',
            'city': 'Москва'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new_user@test.ru').exists())
        # 32.1 проверяем, что пароль сохранился в базе в захешированном виде
        created_user = User.objects.get(email='new_user@test.ru')
        self.assertTrue(created_user.check_password('NewUserPass123!'))

    def test_jwt_login_and_refresh(self):
        # 32.1 проверяем получение пары токенов access и refresh через POST /login/
        login_url = reverse('users:login')
        response = self.client.post(login_url, {
            'email': 'auth_user@test.ru',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # 32.1 проверяем обновление access-токена по refresh-токену через POST /token/refresh/
        refresh_url = reverse('users:token-refresh')
        refresh_response = self.client.post(refresh_url, {
            'refresh': response.data['refresh']
        })
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)


# 32.1 набор тестов для проверки CRUD-операций профиля пользователя и разграничения прав доступа
class UserProfileTestCase(APITestCase):

    def setUp(self):
        # 32.1 создаем владельца профиля и второго авторизованного пользователя
        self.user = User.objects.create(
            email='profile_owner@test.ru',
            first_name='Иван',
            last_name='Иванов',
            city='Казань'
        )
        self.other_user = User.objects.create(
            email='other_profile@test.ru',
            first_name='Петр',
            last_name='Петров'
        )

    def test_user_list_and_unauthorized_access(self):
        # 32.1 проверяем запрет доступа к списку пользователей для неавторизованного запроса
        url = reverse('users:user-list')
        self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

        # 32.1 проверяем получение списка пользователей авторизованным клиентом
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_retrieve_own_vs_other_profile(self):
        # 32.1 проверяем, что при просмотре своего профиля доступны приватные поля (last_name, payments)
        url = reverse('users:user-update', args=(self.user.pk,))
        self.client.force_authenticate(user=self.user)
        own_response = self.client.get(url)
        self.assertEqual(own_response.status_code, status.HTTP_200_OK)
        self.assertIn('last_name', own_response.data)
        self.assertIn('payments', own_response.data)

        # 32.1 проверяем, что при просмотре чужого профиля скрыты приватные поля (UserPublicSerializer)
        self.client.force_authenticate(user=self.other_user)
        other_response = self.client.get(url)
        self.assertEqual(other_response.status_code, status.HTTP_200_OK)
        self.assertNotIn('last_name', other_response.data)
        self.assertNotIn('payments', other_response.data)

    def test_user_update_permissions(self):
        # 32.1 проверяем запрет редактирования чужого профиля (403 Forbidden)
        url = reverse('users:user-update', args=(self.user.pk,))
        self.client.force_authenticate(user=self.other_user)
        forbidden_response = self.client.patch(url, {'city': 'Сочи'})
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

        # 32.1 проверяем успешное редактирование собственного профиля владельцем
        self.client.force_authenticate(user=self.user)
        ok_response = self.client.patch(url, {'city': 'Санкт-Петербург'})
        self.assertEqual(ok_response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, 'Санкт-Петербург')

    def test_user_delete_permissions(self):
        # 32.1 проверяем запрет удаления чужого профиля (403 Forbidden)
        url = reverse('users:user-delete', args=(self.user.pk,))
        self.client.force_authenticate(user=self.other_user)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)

        # 32.1 проверяем успешное удаление собственного профиля владельцем
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())


# 32.1 набор тестов для проверки списка платежей, фильтрации и сортировки
class PaymentTestCase(APITestCase):

    def setUp(self):
        # 32.1 создаем тестового пользователя, курс, урок и два платежа разными способами
        self.user = User.objects.create(email='payer@test.ru')
        self.course = Course.objects.create(title='Python-разработчик', owner=self.user)
        self.lesson = Lesson.objects.create(title='Введение в DRF', course=self.course, owner=self.user)

        self.payment_course = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=15000.00,
            payment_method=Payment.PAYMENT_TRANSFER
        )
        self.payment_lesson = Payment.objects.create(
            user=self.user,
            paid_lesson=self.lesson,
            amount=1500.00,
            payment_method=Payment.PAYMENT_CASH
        )
        self.payments_url = reverse('users:payment-list')

    def test_payments_list_and_filtering(self):
        # 32.1 проверяем запрет просмотра платежей для неавторизованного пользователя
        self.assertEqual(self.client.get(self.payments_url).status_code, status.HTTP_401_UNAUTHORIZED)

        # 32.1 авторизуем пользователя и проверяем получение полного списка платежей
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.payments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # 32.1 проверяем фильтрацию платежей по способу оплаты (cash)
        filter_cash = self.client.get(self.payments_url, {'payment_method': Payment.PAYMENT_CASH})
        self.assertEqual(filter_cash.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filter_cash.data), 1)
        self.assertEqual(filter_cash.data[0]['id'], self.payment_lesson.pk)

        # 32.1 проверяем фильтрацию платежей по оплаченному курсу (paid_course)
        filter_course = self.client.get(self.payments_url, {'paid_course': self.course.pk})
        self.assertEqual(filter_course.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filter_course.data), 1)
        self.assertEqual(filter_course.data[0]['id'], self.payment_course.pk)
