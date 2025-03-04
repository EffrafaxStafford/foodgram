from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet


router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    # path('v1/users/me/', UserMeDetail.as_view()),
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    # path('v1/auth/signup/', UserSignupTokenDetail.as_view()),
    # path('v1/auth/token/', UserSignupTokenDetail.as_view())
]
