from rest_framework import serializers
# 31 импортируем валидатор для проверки уникальности email при регистрации
from rest_framework.validators import UniqueValidator
# 30.2 импортируем модель Payment для создания сериализатора платежей
from users.models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        # 30.2 связываем сериализатор с моделью платежей
        model = Payment
        # 30.2 включаем все поля модели платежей в JSON-представление
        fields = '__all__'


# 31 добавляем сериализатор для безопасной регистрации пользователя с хешированием пароля
class UserRegisterSerializer(serializers.ModelSerializer):
    # 31 настраиваем поле password только для записи, чтобы хеш пароля не возвращался в ответе API
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text='Пароль должен содержать минимум 6 символов'
    )
    # 31 добавляем явную проверку уникальности email с понятным сообщением об ошибке
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже зарегистрирован.'
            )
        ]
    )

    class Meta:
        # 31 связываем сериализатор регистрации с кастомной моделью пользователя
        model = User
        # 31 указываем поля, принимаемые при регистрации нового пользователя
        fields = ('id', 'email', 'password', 'phone', 'city', 'avatar', 'first_name', 'last_name')

    def create(self, validated_data):
        # 31 извлекаем пароль в открытом виде из провалидированных данных
        password = validated_data.pop('password')
        # 31 создаем экземпляр пользователя с остальными полями
        user = User(**validated_data)
        # 31 хешируем пароль перед сохранением в базу данных
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    # 30.2 добавляем вывод списка всех платежей пользователя через обратную связь related_name='payments'
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        # 30.1 связываем сериализатор с моделью пользователя
        model = User
        # 30.2 добавляем поле payments в профиль пользователя для просмотра истории оплат
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'first_name', 'last_name', 'payments')


# 31 добавляем публичный сериализатор профиля без фамилии, пароля и истории платежей для чужих пользователей
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        # 31 связываем публичный сериализатор с моделью пользователя
        model = User
        # 31 оставляем только общую информацию, доступную при просмотре чужого профиля
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'first_name')
