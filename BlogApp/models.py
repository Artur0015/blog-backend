from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, username, password):
        if not username:
            raise ValueError('User must have a username')
        if not password:
            raise ValueError('User must have a password')

        user = self.model(
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=30)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    photo = models.ImageField(blank=True, default='anonym.png')
    about_me = models.TextField(blank=True, default='')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True


class Article(models.Model):
    header = models.CharField(max_length=255, )
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    pub_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_articles')
    dislikes = models.ManyToManyField(User, related_name='disliked_articles')


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    for_article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
