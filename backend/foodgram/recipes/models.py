from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from constants import (MAX_LENGTH_TAG, MAX_LENGTH_INGREDIENT,
                       MAX_LENGTH_UNIT, MAX_LENGTH_RECIPE,
                       MIN_VALUE_COOKING_TIME,
                       MIN_VALUE_INGREDIENT_AMOUNT)


User = get_user_model()


class SelfNameMixin():
    """Миксин для определения __str__ моделей Tags, Ingredients и Recipes."""

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Tags(SelfNameMixin, models.Model):
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
        ordering = ('name',)


class Ingredients(SelfNameMixin, models.Model):
    """Модель для хранения ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_LENGTH_INGREDIENT,
        unique=True)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_UNIT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Recipes(SelfNameMixin, models.Model):
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
        verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)


class IngredientInRecipe(models.Model):
    """Модель для хранения ингредиентов в рецепте и их количества."""

    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингрединет',
        related_name='ingredientinrecipe')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredientinrecipe')
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(MIN_VALUE_INGREDIENT_AMOUNT),))

    def __str__(self):
        return f'{self.ingredient}'

    class Meta:
        verbose_name = 'Ингрединет'
        verbose_name_plural = 'Ингрединеты'


class Favorites(models.Model):
    """Модель для хранения избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='+')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(models.Model):
    """Модель для хранения списка покупок пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist_recipes',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='+')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
