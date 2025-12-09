from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.users.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=8,
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "is_author",
        ]
        read_only_fields = ["id"]

    def validate_username(self, value):
        """Проверка уникальности имени пользователя."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует."
            )
        return value

    def validate_email(self, value):
        """Проверка уникальности email."""
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate(self, data):
        """Проверка совпадения паролей."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают."}
            )
        return data


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для аутентификации пользователя."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        """Проверка учётных данных пользователя."""
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError(
                    "Неверное имя пользователя или пароль."
                )

            if not user.is_active:
                raise serializers.ValidationError("Учётная запись отключена.")

            data["user"] = user
        else:
            raise serializers.ValidationError(
                "Необходимо указать имя пользователя и пароль."
            )

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_author",
            "date_joined",
        ]
        read_only_fields = ["id", "username", "is_author", "date_joined"]


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        min_length=8,
    )
    new_password_confirm = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        """Проверка текущего пароля."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль.")
        return value

    def validate(self, data):
        """Проверка совпадения новых паролей."""
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Пароли не совпадают."}
            )
        return data
