from rest_framework import serializers

from UsersApp.serializers import UserPartialSerializer
from .models import Article


class CommonArticleSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source='likes__count', read_only=True)
    dislikes = serializers.IntegerField(source='dislikes__count', read_only=True)
    author = UserPartialSerializer(read_only=True)


class ArticleListSerializer(CommonArticleSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        extra_kwargs = {
            'text': {'write_only': True},
            'author': {'read_only': True}
        }

    def create(self, validated_data):
        author = self.context['request'].user
        return Article.objects.create(author=author, **validated_data)


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
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return article.likes.filter(id=user.id).exists()

    def get_is_disliked(self, article):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return article.dislikes.filter(id=user.id).exists()
