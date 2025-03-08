from django.urls import include, path
from rest_framework import routers

from .views import (UserAvatarView, UserViewSet,
                    TagsViewSet, IngredientsViewSet,
                    SubscriptionsViewSet, RecipesViewSet)


router = routers.DefaultRouter()
router.register('users/subscriptions', SubscriptionsViewSet,
                basename='subscriptions')
router.register('users', UserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('users/me/avatar/', UserAvatarView.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
