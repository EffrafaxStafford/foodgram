from django.contrib import admin

from .models import Tags, Ingredients, Recipes


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'id')


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')
    search_fields = ('name',)


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'id')
    search_fields = ('name', 'author',)
    filter_fields = ('tags')
