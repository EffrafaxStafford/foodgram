from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import (viewsets, permissions, generics, status)
from djoser.views import UserViewSet as DjoserUserViewSet
# from rest_framework.pagination import LimitOffsetPagination

from .serializers import UserSerializer, UserAvatarSerializer
from .pagination import UsersPagination
from foodgram import settings


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Класс представления для модели User."""

    def get_permissions(self):
        if self.action == "me" and self.request.method == "GET":
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()


class UserAvatarViewSet(generics.UpdateAPIView, generics.DestroyAPIView):
    """Класс представления для работы с полем avatar модели User."""

    serializer_class = UserAvatarSerializer
    http_method_names = ('put', 'delete')

    def get_object(self):
        username = self.request.user.username
        return get_object_or_404(User, username=username)

    def destroy(self, request):
        instance = self.get_object()
        instance.avatar = None
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
