from django.urls import include, path
from rest_framework import routers

from .views import (UserAvatarViewSet, UserViewSet,
                    TagsListViewSet, TagsRetrieveViewSet,)


router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('users/me/avatar/', UserAvatarViewSet.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('tags/', TagsListViewSet.as_view()),
    path('tags/<int:tag_id>/', TagsRetrieveViewSet.as_view()),
]
