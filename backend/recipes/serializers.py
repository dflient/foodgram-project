import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser

from .models import Recipe, RecipeIngridient, Favorite, RecipeTag, ShoppingCart
from tags.models import Tag
from ingridients.models import Ingridient
from users.serializers import UserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='recipe.id', read_only=True
    )
    name = serializers.CharField(
        source='recipe.name', read_only=True
    )
    image = serializers.CharField(
        source='recipe.image', read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='recipe.id', read_only=True
    )
    name = serializers.CharField(
        source='recipe.name', read_only=True
    )
    image = serializers.CharField(
        source='recipe.image', read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeIngridientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingridient.objects.all())
    amount = serializers.FloatField()

    class Meta:
        model = RecipeIngridient
        fields = ['id', 'amount']


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    name = serializers.CharField(source='tag.name', read_only=True)
    color = serializers.CharField(source='tag.color', read_only=True)
    slug = serializers.SlugField(source='tag.slug', read_only=True)

    class Meta:
        model = RecipeTag
        fields = ['id', 'name', 'color', 'slug']


class RecipeSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='description')
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = RecipeIngridientSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, attrs):
        required_fields = [
            'ingredients', 'tags', 'image',
            'name', 'description', 'cooking_time'
        ]

        for field in required_fields:

            if field not in attrs:

                raise serializers.ValidationError(
                    f'Поле {field} не было указано'
                )

        return attrs

    def validate_tags(self, value):
        if len(value) == 0:

            raise serializers.ValidationError

        return value

    def validate_ingredients(self, value):
        if len(value) < 1:

            for item in value:
                amount = item.get('amount')

        else:
            amount = value[0]['amount']

        if len(value) == 0 or amount < 1:

            raise serializers.ValidationError

        return value

    def get_is_favorited(self, instance):
        request = self.context['request']

        if isinstance(request.user, AnonymousUser):
            return False

        if Favorite.objects.filter(
            recipe=instance.id, owner=request.user
        ).exists():
            return True
        else:
            return False

    def get_is_in_shopping_cart(self, instance):
        request = self.context['request']

        if isinstance(request.user, AnonymousUser):
            return False

        if ShoppingCart.objects.filter(
            recipe=instance.id, owner=request.user
        ).exists():
            return True
        else:
            return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            RecipeIngridient.objects.create(
                recipe=recipe, ingredient=ingredient_id, amount=amount
            )

        for tag in tags_data:
            RecipeTag.objects.create(
                recipe=recipe, tag=tag
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()

        if ingredients_data:

            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data['id']
                amount = ingredient_data['amount']
                RecipeIngridient.objects.create(
                    recipe=instance, ingredient=ingredient_id, amount=amount
                )

        if tags_data:
            instance.tags.clear()

            for tag in tags_data:
                RecipeTag.objects.create(
                    recipe=instance, tag=tag
                )

        return instance

    def to_representation(self, instance):
        recipe_obj = super().to_representation(instance)
        ingridients = recipe_obj.get('ingredients')
        tags = recipe_obj.get('tags')
        ingridients_list = []

        for ingridient in ingridients:

            try:
                ingridients_list.append(
                    get_object_or_404(
                        RecipeIngridient, recipe__id=recipe_obj.get('id'),
                        ingredient__id=ingridient.get('id')
                    )
                )
            except Exception as error:

                raise serializers.ValidationError(
                    f'Нельзя использвать один и тот же ингредиент дважды - '
                    f'{error}'
                )

        recipe_obj['ingredients'] = [
            {
                'id': ingridient.ingredient.id,
                'name': ingridient.ingredient.name,
                'measurement_unit': ingridient.ingredient.measurement_unit,
                'amount': ingridient.amount
            } for ingridient in ingridients_list
        ]

        tags_list = []

        for tag in tags:

            try:
                tags_list.append(
                    get_object_or_404(
                        RecipeTag, recipe__id=recipe_obj.get('id'),
                        tag__id=tag
                    )
                )
            except Exception as error:

                raise serializers.ValidationError(
                    f'Нельзя использвать один и тот же ингредиент дважды - '
                    f'{error}'
                )

        recipe_obj['tags'] = [
            {
                'id': tag.tag.id,
                'name': tag.tag.name,
                'color': tag.tag.color,
                'slug': tag.tag.slug
            } for tag in tags_list
        ]

        return recipe_obj
