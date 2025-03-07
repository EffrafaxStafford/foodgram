from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from constants import (MAX_LENGTH_TAG, MAX_LENGTH_INGREDIENT,
                       MAX_LENGTH_UNIT, MAX_LENGTH_RECIPE,
                       MIN_VALUE_COOKING_TIME,
                       MIN_VALUE_INGREDIENT_AMOUNT)


User = get_user_model()


class SelfNameMixin(models.Model):
    """Миксин для определения __str__ моделей Tags, Ingredients и Recipes."""

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Tags(SelfNameMixin):
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


class Ingredients(SelfNameMixin):
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


class Recipes(SelfNameMixin):
    """Модель для хранения рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_LENGTH_RECIPE)
    text = models.TextField(
        verbose_name='Описание')
    image = models.ImageField(
        upload_to='recipes/image/',
        null=True,
        default=None)
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=(MinValueValidator(MIN_VALUE_COOKING_TIME),))
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Тег')
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientRecipe',
        # related_name='recipe',
        verbose_name='Ингредиенты')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    """Модель для хранения ингредиентов в рецепте и их количества."""

    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(MIN_VALUE_INGREDIENT_AMOUNT),),
        default=MIN_VALUE_INGREDIENT_AMOUNT)

    def __str__(self):
        return f'{self.ingredient} для {self.recipe}'
