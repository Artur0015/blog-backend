from django.urls import path

from . import views
from ArticlesApp import views as articles_views

urlpatterns = [
    path('', views.UserRegistration.as_view()),
    path('me/', views.MyUserView.as_view()),
    path('<str:username>/', views.UserInfoView.as_view()),
    path('<str:username>/articles/', articles_views.UserArticlesView.as_view()),
    path('<str:username>/subscribers/', views.UserSubscribersView.as_view())
]
