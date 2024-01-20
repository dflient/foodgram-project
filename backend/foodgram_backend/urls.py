from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from recipes.views import (
    RecipeViewSet,
    FavoriteViewSet,
    ShoppingCartViewSet,
    download_shopping_cart
)
from tags.views import TagViewSet
from ingridients.views import IngredientsViewSet

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/recipes/download_shopping_cart/', download_shopping_cart),
    path('api/recipes/<int:pk>/favorite/', FavoriteViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),
    path('api/recipes/<int:pk>/shopping_cart/', ShoppingCartViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),
    path('api/', include(router.urls)),
    path('api/auth/', include('authentication.urls')),
    path('api/users/', include('users.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
