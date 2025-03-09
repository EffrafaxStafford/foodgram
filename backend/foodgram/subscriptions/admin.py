from django.contrib import admin

from .models import Subscriptions


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription',)
    # fields = ('username', 'email', 'first_name', 'last_name',)
