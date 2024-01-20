from django.urls import path

from .views import get_token, logout

urlpatterns = [
    path('token/login/', get_token),
    path('token/logout/', logout)
]
