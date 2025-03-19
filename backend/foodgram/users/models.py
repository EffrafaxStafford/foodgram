from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import MAX_LENGTH_EMAIL


class FoodgramUserInterface(AbstractUser):
    """Пользовательская модель для пользователей."""

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name='Почта')
    avatar = models.ImageField(
        upload_to='users/avatar/',
        null=True,
        default=None)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
