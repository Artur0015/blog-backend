from django.db import models

from ArticlesApp.models import Article
from UsersApp.models import User


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    for_article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['-id']
