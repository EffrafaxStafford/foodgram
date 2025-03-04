from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUserInterface(AbstractUser):
    """Пользовательская модель для пользователей."""

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
