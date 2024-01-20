from rest_framework import serializers

from .models import Ingridient


class IngridientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        fields = ['id', 'name', 'measurement_unit']
