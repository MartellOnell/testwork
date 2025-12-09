from django.contrib.auth import login, logout
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.users.models import User

from .serializers import (
    ChangePasswordSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet для операций аутентификации.
    """

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "register":
            return UserRegistrationSerializer
        elif self.action == "login":
            return UserLoginSerializer
        elif self.action == "change_password":
            return ChangePasswordSerializer
        return UserSerializer

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        """
        Регистрация нового пользователя.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Удаляем password_confirm перед созданием пользователя
        validated_data = serializer.validated_data.copy()
        validated_data.pop("password_confirm")

        # Создаём пользователя
        user = User.objects.create_user(**validated_data)

        # Создаём токен
        token, created = Token.objects.get_or_create(user=user)

        # Логиним пользователя
        login(request, user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
                "message": "Регистрация прошла успешно.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        """
        Вход в систему.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Получаем или создаём токен
        token, created = Token.objects.get_or_create(user=user)

        # Логиним пользователя
        login(request, user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
                "message": "Вход выполнен успешно.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Выход из системы.
        """
        # Удаляем токен пользователя
        try:
            request.user.auth_token.delete()
        except:
            pass

        # Выполняем logout
        logout(request)

        return Response(
            {"message": "Выход выполнен успешно."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Получение информации о текущем пользователе.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["put", "patch"], permission_classes=[IsAuthenticated]
    )
    def update_profile(self, request):
        """
        Обновление профиля текущего пользователя.
        """
        serializer = UserSerializer(
            request.user, data=request.data, partial=request.method == "PATCH"
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "user": serializer.data,
                "message": "Профиль обновлён успешно.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Смена пароля.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Устанавливаем новый пароль
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        # Пересоздаём токен для безопасности
        try:
            request.user.auth_token.delete()
        except:
            pass
        token = Token.objects.create(user=request.user)

        return Response(
            {
                "message": "Пароль изменён успешно.",
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )
