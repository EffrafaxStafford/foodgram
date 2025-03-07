from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUserInterface(AbstractUser):
    """Пользовательская модель для пользователей."""

    email = models.EmailField(verbose_name='Почта',
                              max_length=255, unique=True)
    avatar = models.ImageField(
        upload_to='users/avatar/',
        null=True,
        default=None)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
