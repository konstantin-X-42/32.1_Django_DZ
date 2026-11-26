from django.contrib import admin
from materials.models import Course, Lesson


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
