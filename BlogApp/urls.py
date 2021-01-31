from django.urls import path
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'articles', views.ArticleViewSet, basename='articles')

urlpatterns = [
    path('articles/<int:id>/comments/', views.CommentsView.as_view()),
    path('user/register/', views.UserRegistartion.as_view()),
    path('user/login/', views.UserLogin.as_view()),
    path('user/info/', views.UserInfo.as_view()),
    path('user/upload/', views.UploadImage.as_view()),
    path('user/<str:username>/info/', views.UserProfile.as_view())
]
urlpatterns += router.urls
