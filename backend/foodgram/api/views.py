from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import (viewsets, permissions, generics, status, filters)
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import Tags, Ingredients
from .serializers import (UserSerializer, UserAvatarSerializer,
                          TagSerializer, IngredientSerializer)
from .pagination import UsersPagination
from foodgram import settings


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Класс представления для модели User."""

    pagination_class = UsersPagination

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


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс представления для работы с тегами."""

    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс представления для работы с ингредиентами."""

    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = Ingredients.objects.all()
        search_field = self.request.query_params.get('name', None)
        print('\n\n', search_field, '\n\n')
        if search_field is not None:
            queryset = queryset.filter(name__startswith=search_field)
        return queryset
