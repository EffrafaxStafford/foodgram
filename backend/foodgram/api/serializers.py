import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer)

from recipes.models import Tags, Ingredients, Recipes, IngredientRecipe
from subscriptions.models import Subscriptions

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Класс поля сериализатора для обрабатки изображения в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializerMixin():
    """Миксин для сериализаторов пользователя."""

    class Meta():
        abstract = True
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')
        fields_only_read = ('id', )
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с полем avatar модели User."""

    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta():
        model = User
        fields = ('avatar',)


class UserSerializer(UserSerializerMixin,
                     UserAvatarSerializer,
                     DjoserUserSerializer):
    """Сериализатор для регистрации пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializerMixin.Meta, DjoserUserSerializer.Meta):
        fields = UserSerializerMixin.Meta().fields + ('avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscriptions.objects.filter(
            user=user, subscription=obj).exists()


class UserCreateSerializer(UserSerializerMixin, DjoserUserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta(UserSerializerMixin.Meta, DjoserUserCreateSerializer.Meta):
        pass


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тегами."""

    class Meta():
        model = Tags
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""

    class Meta():
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с подписками пользователей."""

    subscription = UserSerializer()

    class Meta():
        model = Subscriptions
        fields = ('subscription',)

    def to_representation(self, data):
        representation = super().to_representation(data)
        return representation['subscription']


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами."""

    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta():
        model = Recipes
        fields = '__all__'

    def create(self, validated_data):
        recipe = Recipes.objects.create(**validated_data)

        tads_list = self.initial_data['tags']
        recipe.tags.add(*tads_list)
        ingredients_list = [data['id']
                            for data in self.initial_data['ingredients']]
        recipe.ingredients.add(*ingredients_list)

        for data in self.initial_data['ingredients']:
            obj = IngredientRecipe.objects.get(ingredient_id=data['id'],
                                               recipe=recipe)
            obj.amount = data['amount']
            obj.save()
        return recipe

    def to_representation(self, recipe):
        representation = super().to_representation(recipe)
        for data in representation['ingredients']:
            obj = IngredientRecipe.objects.get(ingredient_id=data['id'],
                                               recipe=recipe)
            data.update({'amount': obj.amount})
        return representation
