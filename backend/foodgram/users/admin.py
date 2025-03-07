from django.contrib import admin

from .models import FoodgramUserInterface


@admin.register(FoodgramUserInterface)
class FoodgramUserInterfaceAdmin(admin.ModelAdmin):
    list_display = ('username', 'id', 'email', 'first_name', 'last_name',)
    fields = ('id', 'username', 'email', 'first_name', 'last_name',)
    search_fields = ('username', 'email')
