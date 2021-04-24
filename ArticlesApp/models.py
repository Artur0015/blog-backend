from django.db import models

from UsersApp.models import User


class Article(models.Model):
    photo = models.ImageField(blank=True)
    header = models.CharField(max_length=255,)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    pub_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_articles')
    dislikes = models.ManyToManyField(User, related_name='disliked_articles')

    class Meta:
        ordering = ['-id']
