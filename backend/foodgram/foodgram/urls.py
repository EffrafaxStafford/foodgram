from api.views import RecipesViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# from .views import short_link
urlpatterns = [
    # path('rcp/<int:recipe_id>/', short_link),
    path('rcp/<int:recipe_id>/', RecipesViewSet.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
