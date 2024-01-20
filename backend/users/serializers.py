from rest_framework import serializers

from recipes.models import User, Recipe
from .models import Follow
from .validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(
        default=False, required=False
    )

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        ]

    def get_object(self):
        pk = self.context['users'].kwargs['pk']
        return User.objects.get(pk=pk)

    def get_is_subscribed(self, obj):
        request = self.context['request']
        following = self.get_object()
        if Follow.objects.filter(
            user=request.user, following__username=following
        ).exists():
            return True


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        max_length=254, required=True
    )
    username = serializers.CharField(
        max_length=150, required=True
    )
    first_name = serializers.CharField(
        max_length=150, required=True
    )
    last_name = serializers.CharField(
        max_length=150, required=True
    )
    password = serializers.CharField(
        max_length=150, required=True, write_only=True
    )

    def validate_username(self, value):
        return validate_username(value)

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        ]


class ResetPasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        max_length=150, required=True, write_only=True
    )
    new_password = serializers.CharField(
        max_length=150, required=True, write_only=True
    )

    class Meta:
        model = User
        fields = ['current_password', 'new_password']


class RecipesInSubscriptionsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


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
        many=True, read_only=True, source='following.recipe'
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
