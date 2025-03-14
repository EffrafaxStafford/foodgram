from django.db.models import F
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, permissions, generics, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from .serializers import (UserAvatarSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          SubscriptionsSerializer,
                          RecipesSerializer,
                          FavoritesSerializer,
                          ShoppingCartSerializer,)
from .pagination import UsersPagination, SubscriptionsPagination, RecipesPagination
from .filters import RecipeFilterSet
from recipes.models import Tags, Ingredients, Recipes, Favorites, ShoppingCart
from subscriptions.models import Subscriptions
from .utils import get_shopping_list


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

        if request.method == 'DELETE':
            Subscriptions.objects.filter(user=user,
                                         subscription=subscription).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = SubscriptionsSerializer(
            data={'user': user.id, 'subscription': subscription.id},
            context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserAvatarView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Вьюшка для обновления и удаления поля avatar модели User."""

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
    pagination_class = RecipesPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().author:
            return super().destroy(request, args, kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def _recipe_detail_post_delete(self, request, pk, MODEL, SERIALIZER):
        user = request.user
        recipe = self.get_object()
        is_exists = MODEL.objects.filter(
            user=user, recipe=recipe).exists()

        if (request.method == 'POST' and is_exists
                or request.method == 'DELETE' and not is_exists):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            MODEL.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = SERIALIZER(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self._recipe_detail_post_delete(
            request, pk, Favorites, FavoritesSerializer)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self._recipe_detail_post_delete(
            request, pk, ShoppingCart, ShoppingCartSerializer)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request, pk=None):
        user = request.user
        recipes = [wishlist.recipe for wishlist in user.wishlist_recipes.all()]

        shopping_list = get_shopping_list(recipes)
        filename = f'{user.username}_shopping_cart'
        with open(filename, 'w+') as file:
            file.write(shopping_list)
            response = HttpResponse(file, content_type='application/txt')
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
            return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        path = '/rcp/' + pk + '/'
        short_link = request.build_absolute_uri(path)
        return Response({'short-link': short_link})
