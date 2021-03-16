from rest_framework import serializers
from .models import Article, Comment, User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class CommonArticleSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source='likes__count', required=False)
    dislikes = serializers.IntegerField(source='dislikes__count', required=False)
    pubDate = serializers.SerializerMethodField()
    author = serializers.CharField(source='author.username', read_only=True)

    def get_pubDate(self, article):
        return article.pub_date.strftime('%d.%m.%Y %H:%M')


class ArticleListSerializer(CommonArticleSerializer):
    text = serializers.CharField(write_only=True)

    class Meta:
        model = Article
        exclude = ('pub_date',)

    def create(self, validated_data):
        header = validated_data['header']
        text = validated_data['text']
        author = self.context['request'].user
        return Article.objects.create(header=header, text=text, author=author)


class ArticleSerializerForProfile(CommonArticleSerializer):
    author = None

    class Meta:
        model = Article
        exclude = ('text', 'author', 'pub_date')


class ArticleRetrieveSerializer(CommonArticleSerializer):
    isLiked = serializers.SerializerMethodField()
    isDisliked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        exclude = ('pub_date',)

    def get_isLiked(self, article):
        return article.likes.filter(id=self.context['request'].user.id).exists()

    def get_isDisliked(self, article):
        return article.dislikes.filter(id=self.context['request'].user.id).exists()

    def update(self, instance, validated_data):
        text = validated_data.get('text')
        header = validated_data.get('header')
        if text:
            instance.text = text
        if header:
            instance.header = header
        instance.save()
        return instance


class BaseUserSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField(read_only=True)

    def get_photo(self, user):
        photo = user.photo.url
        return 'http://127.0.0.1:8000' + photo


class UserSerializer(BaseUserSerializer):
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
        user = User.objects.create_user(username, password)
        return user


class UserProfileSerializer(BaseUserSerializer):
    aboutMe = serializers.CharField(source='about_me')

    class Meta:
        model = User
        fields = ('id', 'username', 'photo', 'aboutMe',)

    def update(self, instance, validated_data):
        instance.about_me = validated_data['about_me']
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False, read_only=True)

    class Meta:
        model = Comment
        exclude = ['for_article']

    def create(self, validated_data):
        text = validated_data['text']
        author = self.context['request'].user
        article_id = self.context['article_id']
        for_article = Article.objects.get(id=article_id)
        comment = Comment.objects.create(text=text, author=author, for_article=for_article)
        return comment


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
