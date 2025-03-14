from django.db.models import F
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer)

from recipes.models import (Tags, Ingredients, Recipes,
                            IngredientInRecipe, Favorites, ShoppingCart)
from subscriptions.models import Subscriptions
from .fields import Base64ImageField
from .utils import create_M2M_recipe_field


User = get_user_model()


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с полем avatar модели User."""

    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta():
        model = User
        fields = ('avatar',)


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


class UserSerializer(UserSerializerMixin,
                     UserAvatarSerializer,
                     DjoserUserSerializer):
    """Сериализатор для регистрации пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializerMixin.Meta, DjoserUserSerializer.Meta):
        fields = UserSerializerMixin.Meta().fields + (
            'avatar', 'is_subscribed')

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


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с IngredientInRecipe."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами."""

    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True, write_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta():
        model = Recipes
        fields = '__all__'

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredient_id_amount = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)

        recipe.tags.set(tags)
        create_M2M_recipe_field(recipe, ingredient_id_amount)
        return recipe

    def update(self, instance, validated_data):
        if self.context['request'].user != instance.author:
            raise PermissionDenied()

        tags = validated_data.pop('tags')
        ingredient_id_amount = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)

        recipe.tags.set(tags)
        recipe.ingredients.clear()
        create_M2M_recipe_field(recipe, ingredient_id_amount)
        return recipe

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Favorites.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=user, recipe=obj).exists()

    def to_representation(self, recipe):
        representation = super().to_representation(recipe)
        representation['tags'] = recipe.tags.all().values()
        representation['ingredients'] = recipe.ingredients.annotate(
            amount=F('ingredientinrecipe__amount')).all().values()
        return representation

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Этот список не может быть пустым.')
        for ingredient in ingredients:
            if (ingredient.get('id') is None
                    or ingredient.get('amount') is None):
                raise serializers.ValidationError(
                    '\'id\' и \'amount\' должны быть заполнены.')
        ingredients_id = [ingredient['id']
                          for ingredient in self.initial_data['ingredients']]
        if len(ingredients_id) != len(set(ingredients_id)):
            raise serializers.ValidationError("Дублирование ингредиентов.")
        return ingredients

    def validate_tags(self, tags):
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Дублирование тегов.')
        return tags

    def validate(self, data):
        if data.get('ingredients') is None:
            raise serializers.ValidationError(
                {'ingredients': 'Обязательное поле.'})
        if data.get('tags') is None:
            raise serializers.ValidationError({'tags': ['Обязательное поле.']})
        return super().validate(data)


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
        recipes = instance.subscription.recipes.all().values(
            'id', 'name', 'image', 'cooking_time')
        recipes_count = len(recipes)

        recipes_limit = self._context['request'].GET.get('recipes_limit')
        if recipes_limit and int(recipes_limit) >= 0:
            recipes = recipes[:int(recipes_limit)]

        representation['subscription']['recipes'] = recipes
        representation['subscription']['recipes_count'] = recipes_count
        return representation['subscription']


class FavoritesShoppingCartMixin(serializers.Serializer):
    """Миксин для сериализаторов моделей Favorites и ShoppingCart."""

    user = UserSerializer(read_only=True)
    recipe = RecipesSerializer(read_only=True)

    class Meta():
        abstract = True
        fields = ('id', 'user', 'recipe',)

    def to_internal_value(self, data):
        data['user'] = User.objects.get(id=data['user'])
        data['recipe'] = Recipes.objects.get(id=data['recipe'])
        return super().to_internal_value(data)

    def create(self, validated_data):
        model = self.Meta.model
        return model.objects.create(user=self.initial_data['user'],
                                    recipe=self.initial_data['recipe'])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        model = self.Meta.model
        favorite = model.objects.values().get(user=instance.user,
                                              recipe=instance.recipe)
        required_fields = ('name', 'image', 'cooking_time')
        representation['recipe'] = {
            k: v for k, v in representation['recipe'].items()
            if k in required_fields}
        representation['recipe']['id'] = favorite['id']
        return representation['recipe']


class FavoritesSerializer(FavoritesShoppingCartMixin):
    """Сериализатор для работы с избранными рецептами пользователей."""

    class Meta(FavoritesShoppingCartMixin.Meta):
        model = Favorites


class ShoppingCartSerializer(FavoritesShoppingCartMixin):
    """Сериализатор для работы со списком покупок пользователей."""

    class Meta(FavoritesShoppingCartMixin.Meta):
        model = ShoppingCart
