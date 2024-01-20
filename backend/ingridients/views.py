from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Ingridient
from .serializers import IngridientSerializer
from .filters import IngredientFilter
from users.permissions import AdminOrReadOnly


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    permission_classes = [AdminOrReadOnly,]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
