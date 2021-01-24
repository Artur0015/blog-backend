from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser


class MyUser(models.Model):
    user = models.OneToOneField(to=User,on_delete=models.CASCADE)
    avatar = models.ImageField(blank=True,default='anonym')


class Article(models.Model):
    header = models.CharField(max_length=255, )
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    for_article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField()

