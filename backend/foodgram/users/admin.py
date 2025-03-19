from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import FoodgramUserInterface


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)


@admin.register(FoodgramUserInterface)
class FoodgramUserInterfaceAdmin(admin.ModelAdmin):
    list_display = ('username', 'id', 'email', 'first_name', 'last_name',)
    fields = ('username', 'email', 'first_name', 'last_name',)
    search_fields = ('username', 'email')
