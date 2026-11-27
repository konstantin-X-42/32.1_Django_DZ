from rest_framework import serializers


class YoutubeValidator:
    # 32.1 инициализируем класс-валидатор и сохраняем имя проверяемого поля
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # 32.1 извлекаем значение проверяемого поля из переданного словаря данных
        url = dict(value).get(self.field)

        # 32.1 проверяем наличие ссылки и убеждаемся, что она ведет только на youtube.com
        if url and 'youtube.com' not in url.lower():
            # 32.1 выбрасываем исключение ValidationError с понятным сообщением об ошибке
            raise serializers.ValidationError(
                'Разрешены только ссылки на видеоматериалы с ресурса youtube.com.'
            )
