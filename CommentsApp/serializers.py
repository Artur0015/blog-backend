from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from ArticlesApp.models import Article
from .models import Comment
from UsersApp.serializers import UserPartialSerializer


class CommentSerializer(ModelSerializer):
    author = UserPartialSerializer(read_only=True)

    class Meta:
        model = Comment
        exclude = ('for_article',)

    def create(self, validated_data):
        text = validated_data['text']
        author = self.context['request'].user
        article_id = self.context['article_id']
        try:
            for_article = Article.objects.only('id').get(id=article_id)
        except ObjectDoesNotExist:
            raise ValidationError()
        return Comment.objects.create(text=text, author=author, for_article=for_article)
