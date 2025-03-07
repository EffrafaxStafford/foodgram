from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import (viewsets, permissions, generics, status, filters, mixins)
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import Tags, Ingredients, Recipes
from subscriptions.models import Subscriptions
from .serializers import (UserAvatarSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          SubscriptionsSerializer,
                          RecipesSerializer,)
from .pagination import UsersPagination, SubscriptionsPagination
from foodgram import settings


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для модели User и подписок пользователей."""

    pagination_class = UsersPagination

    def get_permissions(self):
        if self.action == "me" and self.request.method == "GET":
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        user = request.user
        subscription = self.get_object()
        is_exists = Subscriptions.objects.filter(
            user=user, subscription=subscription).exists()

        if (request.method == 'POST' and is_exists
                or request.method == 'DELETE' and not is_exists
                or user == subscription):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            Subscriptions.objects.create(user=user, subscription=subscription)
            serializer = SubscriptionsSerializer(subscription,
                                                 context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            Subscriptions.objects.filter(
                user=user, subscription=subscription).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class UserAvatarView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Вьюшка для обновления и удаления поля avatar модели User."""

    serializer_class = UserAvatarSerializer
    # http_method_names = ('put', 'delete')

    def get_object(self):
        username = self.request.user.username
        return get_object_or_404(User, username=username)

    def destroy(self, request):
        instance = self.get_object()
        instance.avatar = None
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для перечисления и извлечения тегов."""

    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для перечисления и извлечения ингредиентов."""

    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = Ingredients.objects.all()
        search_field = self.request.query_params.get('name', None)
        if search_field is not None:
            queryset = queryset.filter(name__startswith=search_field)
        return queryset


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """Вьюсет для перечисления подиписчиков пользователя."""

    serializer_class = SubscriptionsSerializer
    pagination_class = SubscriptionsPagination

    def get_queryset(self):
        return Subscriptions.objects.filter(user=self.request.user)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes."""

    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
