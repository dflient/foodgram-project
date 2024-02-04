from colorfield.fields import ColorField
from django.contrib.auth.models import AnonymousUser
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram_backend.constants import MAX_USER_FIELDS_LENGHT
from recipes.models import (Favorite, Ingridient, Recipe, RecipeIngridient,
                            ShoppingCart, Tag)
from users.models import CustomUser, Follow
from .validators import validate_username, validate_recipe_name


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        required=False
    )

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context['request']

        if isinstance(request.user, AnonymousUser):
            return False

        return Follow.objects.filter(
            user=request.user, following__id=obj.id
        ).exists()


class CreateUserSerializer(UserCreateSerializer):

    def validate_username(self, value):
        return validate_username(value)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        ]


class ResetPasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        max_length=MAX_USER_FIELDS_LENGHT,
        required=True, write_only=True
    )
    new_password = serializers.CharField(
        max_length=MAX_USER_FIELDS_LENGHT,
        required=True, write_only=True
    )

    class Meta:
        model = CustomUser
        fields = ['current_password', 'new_password']


class RecipesInSubscriptionsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.image.url if obj.image else ''

        if request is not None:
            return request.build_absolute_uri(image_url)

        return image_url


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='following.id', read_only=True
    )
    email = serializers.CharField(
        source='following.email', read_only=True
    )
    username = serializers.CharField(
        source='following.username', read_only=True
    )
    first_name = serializers.CharField(
        source='following.first_name', read_only=True
    )
    last_name = serializers.CharField(
        source='following.last_name', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField(
        read_only=True
    )
    recipes = RecipesInSubscriptionsSerializer(
        many=True, read_only=True, source='following.recipe',
    )
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Follow
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        ]

    def get_recipes_count(self, obj):
        return len(Recipe.objects.filter(author=obj.following))

    def get_is_subscribed(self, obj):
        return True


class TagSerializer(serializers.ModelSerializer):
    color = ColorField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngridientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        fields = ['id', 'name', 'measurement_unit']


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

    def validate_name(self, value):
        return validate_recipe_name(value)

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

        return Favorite.objects.filter(
            recipe=instance.id, user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, instance):
        request = self.context['request']

        if isinstance(request.user, AnonymousUser):
            return False

        return ShoppingCart.objects.filter(
            recipe=instance.id, user=request.user
        ).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')

        ingredient_names = set()
        for ingredient in ingredients_data:
            name = ingredient.get('id')
            if name in ingredient_names:
                raise serializers.ValidationError(
                    'Нельзя использовать один и тот же ингредиент дважды'
                )
            ingredient_names.add(name)

        tags_data = validated_data.pop('tags')

        tag_names = set()
        for tag_data in tags_data:
            if tag_data in tag_names:
                raise serializers.ValidationError(
                    'Нельзя использовать один и тот же тег дважды'
                )
            tag_names.add(tag_data)

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            RecipeIngridient.objects.create(
                recipe=recipe, ingredient=ingredient_id, amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        instance.tags.clear()
        instance.tags.set(tags_data)

        ingredients_list = []
        for ingredient in ingredients_data:
            name = ingredient.get('id')
            amount = ingredient.get('amount')
            if name in ingredients_list:
                raise serializers.ValidationError(
                    'Нельзя использовать один ингредиент дважды'
                )
            ingredients_list.append((name, amount))

        self.delete_unused_ingredients(instance, ingredients_data)

        for name, amount in ingredients_list:
            try:
                RecipeIngridient.objects.create(
                    recipe=instance.id, ingredient=name, amount=amount
                )
            except Exception:
                RecipeIngridient.objects.filter(
                    recipe_id=instance.id, ingredient=name, amount=amount
                ).delete()
                RecipeIngridient.objects.create(
                    recipe_id=instance.id, ingredient=name, amount=amount
                )

        return instance

    def delete_unused_ingredients(self, instance, ingredients_data):
        ingredients_names = []
        for ingredient in ingredients_data:
            ingredient_obj = ingredient.get('id')
            ingredients_names.append(ingredient_obj.name)

        ingredients_in_recipe = RecipeIngridient.objects.filter(
            recipe_id=instance.id
        )

        for ingredient in ingredients_in_recipe:
            if ingredient.ingredient not in ingredients_names:
                ingredient.delete()

    def to_representation(self, instance):
        recipe_obj = super().to_representation(instance)
        ingridients = recipe_obj.get('ingredients')
        tags = recipe_obj.get('tags')

        tags_list = []

        for tag_id in tags:
            tag_obj = Tag.objects.get(id=tag_id)
            tags_list.append(tag_obj)

        recipe_obj['tags'] = [
            {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            } for tag in tags_list
        ]

        ingridients_list = []

        for ingridient in ingridients:
            ingredint_obj = RecipeIngridient.objects.get(
                recipe_id=recipe_obj.get('id'),
                ingredient_id=ingridient.get('id')
            )
            ingridients_list.append(ingredint_obj)

        recipe_obj['ingredients'] = [
            {
                'id': ingridient.ingredient.id,
                'name': ingridient.ingredient.name,
                'measurement_unit': ingridient.ingredient.measurement_unit,
                'amount': ingridient.amount
            } for ingridient in ingridients_list
        ]

        return recipe_obj
