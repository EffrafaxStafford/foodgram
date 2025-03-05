import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer)


User = get_user_model()


class Base64ImageField(serializers.ImageField):
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
        # TODO
        return False


class UserCreateSerializer(UserSerializerMixin, DjoserUserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta(UserSerializerMixin.Meta, DjoserUserCreateSerializer.Meta):
        pass
