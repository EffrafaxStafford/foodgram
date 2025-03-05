from django.contrib.auth import get_user_model
from django.db import models

from constants import MAX_LENGTH_TAG, MAX_LENGTH_INGREDIENT, MAX_LENGTH_UNIT


User = get_user_model()


class Tags(models.Model):
    """Модель для хранения тегов."""

    name = models.CharField(
        verbose_name='Название тега',
        max_length=MAX_LENGTH_TAG,
        unique=True)
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=MAX_LENGTH_TAG,
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель для хранения ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_LENGTH_INGREDIENT)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_UNIT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name
