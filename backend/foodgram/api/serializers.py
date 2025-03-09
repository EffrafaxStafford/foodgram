import base64

from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer)

from recipes.models import Tags, Ingredients, Recipes, IngredientInRecipe
from subscriptions.models import Subscriptions
from constants import MIN_VALUE_INGREDIENT_AMOUNT

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Класс поля сериализатора для обработки изображения в формате base64."""

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
        read_only_fields = ('id', )
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
        if not user.is_authenticated:
            return False
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


class SubscriptionsSerializer(serializers.Serializer):
    """Сериализатор для работы с подписками пользователей."""

    user = UserSerializer(read_only=True)
    subscription = UserSerializer(read_only=True)

    class Meta():
        model = Subscriptions
        fields = ('user', 'subscription',)

    def to_internal_value(self, data):
        data['user'] = User.objects.get(id=data['user'])
        data['subscription'] = User.objects.get(id=data['subscription'])
        return super().to_internal_value(data)

    def create(self, validated_data):
        return Subscriptions.objects.create(
            user=self.initial_data['user'],
            subscription=self.initial_data['subscription'])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation['subscription']


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами."""

    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        many=True
    )
    amounts = serializers.ListField(
        child=serializers.IntegerField(min_value=MIN_VALUE_INGREDIENT_AMOUNT),
        write_only=True)

    class Meta():
        model = Recipes
        fields = '__all__'

    def to_internal_value(self, data):
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {'ingredients': ["Обязательное поле."]})

        data['amounts'] = [item.get('amount') for item in data['ingredients']]
        data['ingredients'] = [item.get('id') for item in data['ingredients']]
        return super().to_internal_value(data)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        amounts = validated_data.pop('amounts')
        recipe = Recipes.objects.create(**validated_data)

        recipe.tags.set(tags)
        for ingredient, amount in zip(ingredients, amounts):
            recipe.ingredients.add(ingredient,
                                   through_defaults={'amount': amount})
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        amounts = validated_data.pop('amounts')
        recipe = super().update(instance, validated_data)

        recipe.tags.set(tags)
        recipe.ingredients.clear()
        for ingredient, amount in zip(ingredients, amounts):
            recipe.ingredients.add(ingredient,
                                   through_defaults={'amount': amount})
        return recipe

    def to_representation(self, recipe):
        representation = super().to_representation(recipe)
        representation['tags'] = recipe.tags.all().values()

        ingredients = recipe.ingredientinrecipe_set.all().values(
            'ingredient_id', 'ingredient__name',
            'ingredient__measurement_unit', 'amount')

        representation['ingredients'] = [
            {'id': obj['ingredient_id'],
             'name': obj['ingredient__name'],
             'measurement_unit': obj['ingredient__measurement_unit'],
             'amount': obj['amount']} for obj in ingredients]
        return representation
