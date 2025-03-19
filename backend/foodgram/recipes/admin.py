from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Favorites, IngredientInRecipe, Ingredients, Recipes,
                     ShoppingCart, Tags)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'id')


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')
    search_fields = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 0


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'id', 'in_favorites_count')
    fields = ('author', 'name', 'text', 'image', 'preview',
              'cooking_time', 'tags')
    readonly_fields = ('preview',)
    search_fields = ('name', 'author',)
    filter_fields = ('tags',)
    filter_horizontal = ('tags', 'ingredients')
    inlines = (IngredientInRecipeInline,)

    @admin.display(description="В списке избранных")
    def in_favorites_count(self, obj, verbose_name='Рецепт'):
        return obj.users.count()

    def preview(self, obj):
        return mark_safe(
            f'<img src="{obj.image.url}" style="max-height: 200px;">')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
