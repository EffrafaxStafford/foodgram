from django.contrib.auth import get_user_model
from django.db import models

from constants import MAX_LENGTH


User = get_user_model()


class Tags(models.Model):
    """Модель для хранения тегов."""

    name = models.CharField(max_length=MAX_LENGTH, unique=True)
    slug = models.SlugField(max_length=MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
