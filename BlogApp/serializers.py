from rest_framework import serializers
from .models import Article, Comment, User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class CommonArticleSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source='likes__count', required=False)
    dislikes = serializers.IntegerField(source='dislikes__count', required=False)
    pub_date = serializers.SerializerMethodField()
    author = serializers.CharField(source='author.username', read_only=True)

    def get_pub_date(self, article):
        return article.pub_date.strftime('%d.%m.%Y %H:%M')


class ArticleListSerializer(CommonArticleSerializer):
    text = serializers.CharField(write_only=True)

    class Meta:
        model = Article
        fields = '__all__'

    def create(self, validated_data):
        header = validated_data['header']
        text = validated_data['text']
        author = self.context['request'].user
        return Article.objects.create(header=header, text=text, author=author)


class ArticleSerializerForProfile(CommonArticleSerializer):
    author = None

    class Meta:
        model = Article
        exclude = ('text', 'author')


class ArticleRetrieveSerializer(CommonArticleSerializer):
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'

    def get_is_liked(self, article):
        return article.likes.filter(id=self.context['request'].user.id).exists()

    def get_is_disliked(self, article):
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


class UserSerializer(serializers.ModelSerializer):
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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'photo', 'about_me')

    def update(self, instance, validated_data):
        about_me = validated_data.get('about_me')
        if about_me:
            instance.about_me = about_me
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
    remember_me = serializers.BooleanField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise AuthenticationFailed({'detail': 'Invalid Credentials'})

        return {"user": user, 'remember_me': attrs['remember_me']}


class ImageUploadSerializer(serializers.Serializer):
    photo = serializers.ImageField()

    def create(self, validated_data):
        user = self.context['request'].user
        user.photo = validated_data['photo']
        user.save()
        return user
