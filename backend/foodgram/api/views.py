from django.contrib.auth import get_user_model
from rest_framework import viewsets


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Класс представления для модели User."""
