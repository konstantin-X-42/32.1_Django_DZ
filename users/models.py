from django.contrib.auth.models import AbstractUser
from django.db import models
# 30.2 импортируем модели Course и Lesson для связи с платежами
from materials.models import Course, Lesson


class User(AbstractUser):
    # 30.1 отключаем стандартное поле username, так как авторизация будет происходить по email
    username = None

    # 30.1 переопределяем поле email, делая его уникальным для использования в качестве логина
    email = models.EmailField(
        unique=True,
        verbose_name='Почта',
        help_text='Укажите почту'
    )

    # 30.1 добавляем необязательное поле для номера телефона пользователя
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name='Телефон',
        help_text='Укажите телефон'
    )

    # 30.1 добавляем необязательное поле для города проживания пользователя
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Город',
        help_text='Укажите город'
    )

    # 30.1 добавляем необязательное поле для загрузки аватара пользователя
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Загрузите аватар'
    )

    # 30.1 устанавливаем поле email в качестве основного идентификатора при входе в систему
    USERNAME_FIELD = 'email'

    # 30.1 убираем обязательные дополнительные поля при создании суперпользователя через консоль
    REQUIRED_FIELDS = []

    class Meta:
        # 30.1 задаем человекочитаемые названия модели в единственном и множественном числе для админки
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        # 30.1 возвращаем email пользователя при строковом представлении объекта
        return self.email


class Payment(models.Model):
    # 30.2 определяем доступные способы оплаты через константы и кортеж вариантов выбора
    PAYMENT_CASH = 'cash'
    PAYMENT_TRANSFER = 'transfer'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_CASH, 'Наличные'),
        (PAYMENT_TRANSFER, 'Перевод на счет'),
    ]

    # 30.2 связываем платеж с конкретным пользователем через внешний ключ
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь',
        help_text='Выберите пользователя, совершившего оплату'
    )

    # 30.2 добавляем поле даты и времени оплаты с автоматической фиксацией при создании записи
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты',
        help_text='Дата и время проведения платежа'
    )

    # 30.2 добавляем необязательную ссылку на оплаченный курс
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='Оплаченный курс',
        help_text='Выберите курс, если оплачен курс целиком'
    )

    # 30.2 добавляем необязательную ссылку на отдельно оплаченный урок
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='Оплаченный урок',
        help_text='Выберите урок, если оплачен отдельный урок'
    )

    # 30.2 добавляем поле суммы оплаты с фиксированной точностью до копеек
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты',
        help_text='Укажите сумму платежа'
    )

    # 30.2 добавляем поле выбора способа оплаты (наличные или перевод на счет)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_TRANSFER,
        verbose_name='Способ оплаты',
        help_text='Выберите способ оплаты'
    )

    class Meta:
        # 30.2 задаем человекочитаемые названия модели платежей для административной панели
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        # 30.2 устанавливаем сортировку по умолчанию от самых новых платежей к старым
        ordering = ('-payment_date',)

    def __str__(self):
        # 30.2 возвращаем информативное строковое представление платежа
        target = self.paid_course if self.paid_course else self.paid_lesson
        return f'{self.user.email} — {target} ({self.amount} руб.)'
