from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя для системы UGC опросов.
    """

    is_author = models.BooleanField(
        default=False,
        verbose_name="Is Author",
    )

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.username
