from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password as validate_user_password
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from .models import User


class UserSerializer(ModelSerializer):
    times_liked = serializers.IntegerField(source='articles__likes__count')
    times_disliked = serializers.IntegerField(source='articles__dislikes__count')

    class Meta:
        model = User
        fields = ('id', 'username', 'photo', 'about_me', 'date_joined', 'times_liked', 'times_disliked')


class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        return User.objects.create_user(username, password, **validated_data)

    def validate_password(self, value):
        validate_user_password(value)
        return value


class UserPartialSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'photo', 'about_me')
        extra_kwargs = {'about_me': {'write_only': True}}

    def validate_username(self, username):  # username is not validated automatically if request method is PATCH
        if User.objects.filter(username=username):
            raise ValidationError('User with such username already exists')
        return username


class LoginSerializer(Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise AuthenticationFailed()
        return {'user': user}
