from django.urls import include, path
from rest_framework import routers

from .views import (ChangePasswordViewSet, FavoriteViewSet, IngredientsViewSet,
                    RecipeViewSet, ShoppingCartViewSet, SubscribeViewSet,
                    SubscriptionsListViewSet, TagViewSet, UserViewSet,
                    download_shopping_cart, get_token, logout)

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart),
    path('recipes/<int:pk>/favorite/', FavoriteViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),
    path('users/set_password/', ChangePasswordViewSet.as_view({'post': 'create'})),
    path('users/subscriptions/', SubscriptionsListViewSet.as_view({'get': 'list'})),
    path('users/<int:pk>/subscribe/', SubscribeViewSet.as_view({
        'post': 'create', 'delete': 'destroy'
    })),
    path('token/login/', get_token),
    path('token/logout/', logout),
    path('', include(router.urls))
]
