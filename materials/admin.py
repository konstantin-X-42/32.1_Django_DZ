from django.contrib import admin
# 32.1 импортируем модель Subscription для регистрации в административной панели
from materials.models import Course, Lesson, Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # 31 добавляем отображение владельца курса в списке объектов административной панели
    list_display = ('id', 'title', 'owner')
    # 31 добавляем фильтр по владельцу для удобного поиска в админке
    list_filter = ('owner',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    # 31 добавляем отображение владельца урока в списке объектов административной панели
    list_display = ('id', 'title', 'course', 'owner')
    # 31 добавляем фильтрацию по курсу и владельцу в админке
    list_filter = ('course', 'owner')


# 32.1 регистрируем модель подписок пользователей на курсы в административной панели
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    # 32.1 настраиваем отображение полей подписки в списке объектов админки
    list_display = ('id', 'user', 'course')
    # 32.1 добавляем фильтрацию по пользователю и курсу для удобного поиска в админке
    list_filter = ('user', 'course')
