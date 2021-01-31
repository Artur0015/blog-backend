from rest_framework import serializers
from .models import Article, Comment, User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed, NotFound
from django.core.paginator import Paginator, EmptyPage

from .paginators import ArticlePaginatorForProfile
from .utils import UsernameAlreadyExistsError


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

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


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        exclude = ['for_article', 'id']

    def create(self, validated_data):
        text = validated_data['text']
        author = self.context['request'].user
        article_id = self.context['request'].resolver_match.kwargs.get('id')
        for_article = Article.objects.get(id=article_id)
        comment = Comment.objects.create(text=text, author=author, for_article=for_article)
        return comment


class BaseUserSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField(read_only=True)

    def get_photo(self, user):
        photo = user.photo.url
        return 'http://127.0.0.1:8000' + photo


class MyUserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'photo', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        try:
            User.objects.get_by_natural_key(username)
            raise UsernameAlreadyExistsError()
        except ObjectDoesNotExist:
            user = User.objects.create_user(username=username, password=password)
        return user


class UserProfileSerializer(BaseUserSerializer):
    aboutMe = serializers.CharField(source='about_me')
    articles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'photo', 'aboutMe', 'articles')
        extra_kwargs = {
            'username': {'read_only': True}
        }

    def update(self, instance, validated_data):
        instance.about_me = validated_data['about_me']
        instance.save()
        return instance

    def get_articles(self, obj):
        articles = obj.article_set.all()
        paginator = ArticlePaginatorForProfile()
        page = paginator.paginate_queryset(articles, self.context['request'])
        serializer = ArticleSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data).data


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
    photo = serializers.ImageField()

    def create(self, validated_data):
        user = self.context['request'].user
        user.photo = validated_data['photo']
        user.save()
        return user

    def to_representation(self, instance):
        return {'photo': 'http://127.0.0.1:8000' + instance.photo.url}
