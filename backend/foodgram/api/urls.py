from django.urls import include, path
from rest_framework import routers

from .views import UserAvatarViewSet, UserViewSet


router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('users/me/avatar/', UserAvatarViewSet.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    # path('/auth/signup/', UserSignupTokenDetail.as_view()),
    # path('/auth/token/', UserSignupTokenDetail.as_view())
]
