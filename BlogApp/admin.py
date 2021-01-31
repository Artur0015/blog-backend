from django.contrib import admin
from .models import Article, Comment, User

admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(User)
