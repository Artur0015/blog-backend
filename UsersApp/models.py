from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator, MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

username_validator = RegexValidator('^[a-zA-Z0-9_]*$',
                                    'Username must consisting only of letters, numbers and underscores')


class UserManager(BaseUserManager):
    def create_user(self, username, password, **kwargs):
        if not username:
            raise ValueError('User must have a username')
        if not password:
            raise ValueError('User must have a password')

        user = self.model(username=username, **kwargs)
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
    username = models.CharField(unique=True, max_length=12, validators=[MinLengthValidator(6), username_validator])
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    photo = models.ImageField(blank=True, null=True)
    about_me = models.TextField(blank=True, default='', null=True)
    subscriptions = models.ManyToManyField('self', related_name='subscribers', symmetrical=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True
