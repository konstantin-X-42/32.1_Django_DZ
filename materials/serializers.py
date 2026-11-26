from rest_framework import serializers
from materials.models import Course, Lesson
# 32.1 импортируем кастомный валидатор для проверки ссылок на youtube.com
from materials.validators import YoutubeValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        # 30.1 связываем сериализатор с моделью урока
        model = Lesson
        # 30.1 включаем все поля модели урока в JSON-представление
        fields = '__all__'
        # 32.1 подключаем валидатор YoutubeValidator для проверки поля video_url
        validators = [YoutubeValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    # 30.2 создаем вычисляемое поле для вывода количества уроков в курсе через SerializerMethodField
    lessons_count = serializers.SerializerMethodField()
    # 30.2 добавляем вложенный сериализатор для вывода списка всех уроков, связанных с курсом через related_name='lessons'
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        # 30.1 связываем сериализатор с моделью курса
        model = Course
        # 30.1 включаем все поля модели курса в JSON-представление
        fields = '__all__'

    def get_lessons_count(self, obj):
        # 30.2 подсчитываем количество связанных уроков через обратную связь related_name='lessons'
        return obj.lessons.count()


#-----32.1---


# from rest_framework import serializers
# from materials.models import Course, Lesson
#
#
# class LessonSerializer(serializers.ModelSerializer):
#     class Meta:
#         # 30.1 связываем сериализатор с моделью урока
#         model = Lesson
#         # 30.1 включаем все поля модели урока в JSON-представление
#         fields = '__all__'
#
#
# class CourseSerializer(serializers.ModelSerializer):
#     # 30.2 создаем вычисляемое поле для вывода количества уроков в курсе через SerializerMethodField
#     lessons_count = serializers.SerializerMethodField()
#     # 30.2 добавляем вложенный сериализатор для вывода списка всех уроков, связанных с курсом через related_name='lessons'
#     lessons = LessonSerializer(many=True, read_only=True)
#
#     class Meta:
#         # 30.1 связываем сериализатор с моделью курса
#         model = Course
#         # 30.1 включаем все поля модели курса в JSON-представление
#         fields = '__all__'
#
#     def get_lessons_count(self, obj):
#         # 30.2 подсчитываем количество связанных уроков через обратную связь related_name='lessons'
#         return obj.lessons.count()
