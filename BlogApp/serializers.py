from rest_framework import serializers
from .models import Article, Comment, User, MyUser
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

from .utils import UsernameAlreadyExistsError


def check_ownership(request, obj):
    return request.user == obj.author


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    isOwner = serializers.SerializerMethodField('get_owner')

    class Meta:
        model = Article
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text')
        instance.header = validated_data.get('header')
        instance.save()
        return instance

    def create(self, validated_data):
        header = validated_data['header']
        text = validated_data['text']
        author = self.context['request'].user
        return Article.objects.create(header=header, text=text, author=author)

    def get_owner(self, obj):
        return check_ownership(self.context['request'], obj)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    isOwner = serializers.SerializerMethodField('get_owner')

    class Meta:
        model = Comment
        exclude = ['for_article', 'id']

    def create(self, validated_data):
        text = validated_data['text']
        author = self.context['request'].user
        for_article = Article.objects.get(pk=self.context['article_id'])
        return Comment.objects.create(text=text, author=author, for_article=for_article)

    def get_owner(self, obj):
        return check_ownership(self.context['request'], obj)


class UserSerializer(serializers.ModelSerializer):
    isAuthenticated = serializers.BooleanField(source='user.is_authenticated', read_only=True)
    username = serializers.CharField(source='user.username')
    photo = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(source='user.password', write_only=True)

    class Meta:
        model = MyUser
        fields = ('username', 'isAuthenticated', 'photo', 'password')

    def create(self, validated_data):
        username = validated_data['user']['username']
        password = validated_data['user']['password']
        try:
            User.objects.get_by_natural_key(username)
            raise UsernameAlreadyExistsError()
        except ObjectDoesNotExist:
            user = User.objects.create_user(username=username, password=password)
            my_user = MyUser.objects.create(user=user)
        return my_user

    def get_photo(self, user):
        photo = user.avatar.url
        return 'http://127.0.0.1:8000' + photo


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    rememberMe = serializers.BooleanField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise AuthenticationFailed({'detail': 'Invalid Credentials'})

        return {"user": user, 'remember_me': attrs['rememberMe']}


class ImageUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

    def create(self, validated_data):
        user = MyUser.objects.get(user=self.context['request'].user)
        user.avatar = validated_data['avatar']
        user.save()
        return user

    def to_representation(self, instance):
        return {'avatar': 'http://127.0.0.1:8000' + instance.avatar.url}
