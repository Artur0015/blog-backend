from django.urls import path

from . import views
from CommentsApp import views as comments_views


urlpatterns = [
    path('', views.ArticleListCreateView.as_view()),
    path('<int:pk>/', views.ArticleUpdateDestroyRetrieveView.as_view()),
    path('<int:pk>/comments/', comments_views.CommentsListCreateView.as_view()),
    path('<int:pk>/dislikes/', views.ArticleDislikesView.as_view()),
    path('<int:pk>/likes/', views.ArticleLikesView.as_view()),
]
