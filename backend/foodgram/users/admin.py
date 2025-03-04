from django.contrib import admin

from .models import FoodgramUserInterface


@admin.register(FoodgramUserInterface)
class FoodgramUserInterfaceAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',)
    fields = ('username', 'email', 'first_name', 'last_name',)
    search_fields = ('username',)
