from django.core.management.base import BaseCommand
from materials.models import Course, Lesson
from users.models import User, Payment


class Command(BaseCommand):
    # 30.2 задаем краткое описание кастомной команды для справки manage.py help
    help = 'Заполняет базу данных тестовыми курсами, уроками и платежами'

    def handle(self, *args, **options):
        # 30.2 получаем первого пользователя из базы или создаем тестового при его отсутствии
        user, _ = User.objects.get_or_create(
            email='student@mail.ru',
            defaults={'city': 'Москва', 'phone': '+79991112233'}
        )

        # 30.2 создаем или получаем тестовые курсы для привязки к платежам
        course_python, _ = Course.objects.get_or_create(
            title='Python-разработчик',
            defaults={'description': 'Полный курс по разработке на Python и Django'}
        )
        course_drf, _ = Course.objects.get_or_create(
            title='Django REST Framework',
            defaults={'description': 'Создание современных API на DRF'}
        )

        # 30.2 создаем или получаем тестовые уроки для привязки к платежам
        lesson_models, _ = Lesson.objects.get_or_create(
            title='Модели и ORM в Django',
            course=course_python,
            defaults={'description': 'Урок по проектированию моделей базы данных'}
        )
        lesson_serializers, _ = Lesson.objects.get_or_create(
            title='Сериализаторы и ViewSet',
            course=course_drf,
            defaults={'description': 'Урок по работе с SerializerMethodField'}
        )

        # 30.2 формируем список тестовых платежей с разными способами оплаты и объектами (курсы и уроки)
        payments_data = [
            {
                'user': user,
                'paid_course': course_python,
                'paid_lesson': None,
                'amount': 45000.00,
                'payment_method': Payment.PAYMENT_TRANSFER,
            },
            {
                'user': user,
                'paid_course': None,
                'paid_lesson': lesson_models,
                'amount': 2500.00,
                'payment_method': Payment.PAYMENT_CASH,
            },
            {
                'user': user,
                'paid_course': course_drf,
                'paid_lesson': None,
                'amount': 30000.00,
                'payment_method': Payment.PAYMENT_TRANSFER,
            },
            {
                'user': user,
                'paid_course': None,
                'paid_lesson': lesson_serializers,
                'amount': 3000.00,
                'payment_method': Payment.PAYMENT_CASH,
            },
        ]

        # 30.2 записываем созданные платежи в базу данных
        for item in payments_data:
            Payment.objects.create(**item)

        # 30.2 выводим сообщение об успешном наполнении таблицы платежей в консоль
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена тестовыми платежами!'))
