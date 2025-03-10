from django.contrib import admin

from .models import (Tags, Ingredients, Recipes, IngredientInRecipe,
                     Favorites, ShoppingCart)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'id')


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')
    search_fields = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 0


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'id',)
    search_fields = ('name', 'author',)
    filter_fields = ('tags')
    inlines = (IngredientInRecipeInline,)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
