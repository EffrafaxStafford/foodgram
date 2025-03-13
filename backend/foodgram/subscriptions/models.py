from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Subscriptions(models.Model):
    """Модель для хранения подписок пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик')
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписка',
        related_name='+')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscription'], name="unique_subscription",),
        ]
