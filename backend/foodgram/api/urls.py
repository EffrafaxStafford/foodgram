from django.urls import include, path
from rest_framework import routers

from .views import (UserAvatarViewSet, UserViewSet,
                    TagsViewSet, IngredientsViewSet,)


router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('users/me/avatar/', UserAvatarViewSet.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
