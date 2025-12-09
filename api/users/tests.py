from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Тесты регистрации пользователя."""

    def setUp(self):
        self.register_url = reverse("auth-register")
        self.valid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "is_author": False,
        }

    def test_register_user_success(self):
        """Тест успешной регистрации пользователя."""
        response = self.client.post(self.register_url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

        # Проверяем, что пользователь создан
        self.assertTrue(User.objects.filter(username="testuser").exists())

        # Проверяем, что токен создан
        user = User.objects.get(username="testuser")
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_register_author_success(self):
        """Тест регистрации автора."""
        data = self.valid_data.copy()
        data["is_author"] = True

        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="testuser")
        self.assertTrue(user.is_author)

    def test_register_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями."""
        data = self.valid_data.copy()
        data["password_confirm"] = "wrongpassword"

        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_register_duplicate_username(self):
        """Тест регистрации с существующим username."""
        User.objects.create_user(username="testuser", password="testpass")

        response = self.client.post(self.register_url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_duplicate_email(self):
        """Тест регистрации с существующим email."""
        User.objects.create_user(
            username="otheruser", email="testuser@example.com", password="testpass"
        )

        response = self.client.post(self.register_url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_short_password(self):
        """Тест регистрации со слишком коротким паролем."""
        data = self.valid_data.copy()
        data["password"] = "short"
        data["password_confirm"] = "short"

        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """Тест регистрации с отсутствующими полями."""
        response = self.client.post(self.register_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)


class UserLoginTestCase(APITestCase):
    """Тесты входа в систему."""

    def setUp(self):
        self.login_url = reverse("auth-login")
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
            is_author=False,
        )

    def test_login_success(self):
        """Тест успешного входа."""
        data = {"username": "testuser", "password": "testpass123"}

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_login_wrong_password(self):
        """Тест входа с неверным паролем."""
        data = {"username": "testuser", "password": "wrongpassword"}

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_username(self):
        """Тест входа с несуществующим пользователем."""
        data = {"username": "nonexistent", "password": "testpass123"}

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """Тест входа неактивного пользователя."""
        self.user.is_active = False
        self.user.save()

        data = {"username": "testuser", "password": "testpass123"}

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_creates_token(self):
        """Тест создания токена при входе."""
        data = {"username": "testuser", "password": "testpass123"}

        # Убеждаемся, что токена нет
        self.assertFalse(Token.objects.filter(user=self.user).exists())

        response = self.client.post(self.login_url, data, format="json")

        # Проверяем, что токен создан
        self.assertTrue(Token.objects.filter(user=self.user).exists())
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data["token"], token.key)


class UserLogoutTestCase(APITestCase):
    """Тесты выхода из системы."""

    def setUp(self):
        self.logout_url = reverse("auth-logout")
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_logout_success(self):
        """Тест успешного выхода."""
        response = self.client.post(self.logout_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что токен удалён
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_unauthenticated(self):
        """Тест выхода без аутентификации."""
        self.client.credentials()  # Убираем авторизацию

        response = self.client.post(self.logout_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserMeTestCase(APITestCase):
    """Тесты получения информации о текущем пользователе."""

    def setUp(self):
        self.me_url = reverse("auth-me")
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_author=True,
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_get_me_success(self):
        """Тест получения информации о текущем пользователе."""
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "testuser@example.com")
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")
        self.assertTrue(response.data["is_author"])

    def test_get_me_unauthenticated(self):
        """Тест получения информации без аутентификации."""
        self.client.credentials()  # Убираем авторизацию

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UpdateProfileTestCase(APITestCase):
    """Тесты обновления профиля."""

    def setUp(self):
        self.update_url = reverse("auth-update-profile")
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_update_profile_success(self):
        """Тест успешного обновления профиля."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
        }

        response = self.client.put(self.update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(self.user.email, "updated@example.com")

    def test_partial_update_profile(self):
        """Тест частичного обновления профиля."""
        data = {"first_name": "Updated"}

        response = self.client.patch(self.update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "User")  # Не изменилось

    def test_update_profile_unauthenticated(self):
        """Тест обновления профиля без аутентификации."""
        self.client.credentials()  # Убираем авторизацию

        response = self.client.put(self.update_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordTestCase(APITestCase):
    """Тесты смены пароля."""

    def setUp(self):
        self.change_password_url = reverse("auth-change-password")
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="oldpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_change_password_success(self):
        """Тест успешной смены пароля."""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }

        old_token = self.token.key
        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

        # Проверяем, что пароль изменён
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

        # Проверяем, что старый токен удалён
        self.assertFalse(Token.objects.filter(key=old_token).exists())

        # Проверяем, что создан новый токен
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_change_password_wrong_old_password(self):
        """Тест смены пароля с неверным старым паролем."""
        data = {
            "old_password": "wrongpass",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }

        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """Тест смены пароля с несовпадающими новыми паролями."""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "differentpass",
        }

        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_too_short(self):
        """Тест смены пароля на слишком короткий."""
        data = {
            "old_password": "oldpass123",
            "new_password": "short",
            "new_password_confirm": "short",
        }

        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        """Тест смены пароля без аутентификации."""
        self.client.credentials()  # Убираем авторизацию

        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }

        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenAuthenticationTestCase(APITestCase):
    """Тесты аутентификации по токену."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.me_url = reverse("auth-me")

    def test_access_with_valid_token(self):
        """Тест доступа с валидным токеном."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_with_invalid_token(self):
        """Тест доступа с невалидным токеном."""
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid_token_key")

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_without_token(self):
        """Тест доступа без токена."""
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_with_wrong_auth_type(self):
        """Тест доступа с неправильным типом авторизации."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.key}")

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
