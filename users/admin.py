from django.contrib import admin
# 30.2 импортируем модель Payment и User
from users.models import User, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 30.1 настраиваем отображение полей пользователя в списке объектов административной панели
    list_display = ('id', 'email', 'phone', 'city', 'is_active')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # 30.2 настраиваем отображение списка платежей в административной панели
    list_display = ('id', 'user', 'payment_date', 'paid_course', 'paid_lesson', 'amount', 'payment_method')
    # 30.2 добавляем фильтрацию по способу оплаты в админке
    list_filter = ('payment_method',)
