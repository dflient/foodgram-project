from django_filters import rest_framework as rest_framework_filters

from .models import Ingridient


class IngredientFilter(rest_framework_filters.FilterSet):
    name = rest_framework_filters.CharFilter(
        lookup_expr='icontains', field_name='name'
    )

    class Meta:
        model = Ingridient
        fields = ('name',)
