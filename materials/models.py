# 31 импортируем настройки проекта для ссылки на кастомную модель пользователя AUTH_USER_MODEL
from django.conf import settings
from django.db import models


class Course(models.Model):
    # 30.1 создаем обязательное текстовое поле для названия курса
    title = models.CharField(
        max_length=150,
        verbose_name='Название курса',
        help_text='Укажите название курса'
    )

    # 30.1 создаем необязательное поле для загрузки превью-изображения курса
    preview = models.ImageField(
        upload_to='materials/courses/previews/',
        blank=True,
        null=True,
        verbose_name='Превью',
        help_text='Загрузите превью курса'
    )

    # 30.1 создаем необязательное текстовое поле для подробного описания курса
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание курса',
        help_text='Укажите описание курса'
    )

    # 31 добавляем связь с владельцем курса (пользователем, создавшим курс)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='courses',
        verbose_name='Владелец',
        help_text='Укажите владельца курса'
    )

    class Meta:
        # 30.1 задаем человекочитаемые названия модели курса для административной панели
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        # 30.1 возвращаем название курса при строковом представлении объекта
        return self.title


class Lesson(models.Model):
    # 30.1 создаем обязательное текстовое поле для названия урока
    title = models.CharField(
        max_length=150,
        verbose_name='Название урока',
        help_text='Укажите название урока'
    )

    # 30.1 создаем необязательное текстовое поле для описания содержания урока
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание урока',
        help_text='Укажите описание урока'
    )

    # 30.1 создаем необязательное поле для загрузки превью-изображения урока
    preview = models.ImageField(
        upload_to='materials/lessons/previews/',
        blank=True,
        null=True,
        verbose_name='Превью',
        help_text='Загрузите превью урока'
    )

    # 30.1 создаем поле для хранения URL-ссылки на видеоматериал урока
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на видео',
        help_text='Укажите ссылку на видео'
    )

    # 30.1 связываем урок с конкретным курсом через внешний ключ с каскадным удалением
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        blank=True,
        null=True,
        verbose_name='Курс',
        help_text='Выберите курс, к которому относится урок'
    )

    # 31 добавляем связь с владельцем урока (пользователем, создавшим урок)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='lessons',
        verbose_name='Владелец',
        help_text='Укажите владельца урока'
    )

    class Meta:
        # 30.1 задаем человекочитаемые названия модели урока для административной панели
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        # 30.1 возвращаем название урока при строковом представлении объекта
        return self.title


# 32.1 добавляем модель подписки пользователя на обновления курса
class Subscription(models.Model):
    # 32.1 связываем подписку с пользователем через внешний ключ
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )

    # 32.1 связываем подписку с курсом через внешний ключ
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Курс',
        help_text='Выберите курс для подписки'
    )

    class Meta:
        # 32.1 задаем человекочитаемые названия модели подписки для административной панели
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        # 32.1 гарантируем уникальность пары ID пользователя и ID курса на уровне базы данных
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_subscription')
        ]

    def __str__(self):
        # 32.1 возвращаем информативное строковое представление подписки
        return f'{self.user} — {self.course}'
