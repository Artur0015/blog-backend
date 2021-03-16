from django.urls import path
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'articles', views.ArticleViewSet, basename='articles')

urlpatterns = [
    path('articles/<int:pk>/comments/', views.CommentsView.as_view()),
    path('articles/<int:pk>/dislikes/', views.ArticleDislikesView.as_view()),
    path('articles/<int:pk>/likes/', views.ArticleLikesView.as_view()),
    path('comments/<int:pk>/', views.CommentDeleteView.as_view()),
    path('user/register/', views.UserRegistration.as_view()),
    path('user/login/', views.UserLogin.as_view()),
    path('user/info/', views.UserInfo.as_view()),
    path('user/upload/', views.UploadImage.as_view()),
    path('user/<str:username>/info/', views.UserProfile.as_view()),
    path('user/<str:username>/articles/', views.UserArticles.as_view()),
]
urlpatterns += router.urls
