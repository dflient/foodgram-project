from django.urls import include, path
from rest_framework import routers

from .views import (ChangePasswordViewSet, SubscribeViewSet,
                    SubscriptionsListViewSet, UserViewSet)

user_router = routers.DefaultRouter()
user_router.register(r'', UserViewSet)


urlpatterns = [
    path('set_password/', ChangePasswordViewSet.as_view({'post': 'create'})),
    path('subscriptions/', SubscriptionsListViewSet.as_view({'get': 'list'})),
    path('<int:pk>/subscribe/', SubscribeViewSet.as_view({
        'post': 'create', 'delete': 'destroy'
    })),
    path('', include(user_router.urls)),
]
