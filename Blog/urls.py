from django.urls import include, path

from ArticlesApp import views as articles_views
from UsersApp import views as users_views
from UsersApp.views import UserAuthToken

urlpatterns = {
    path('api/articles/', include('ArticlesApp.urls')),
    path('api/users/', include('UsersApp.urls')),
    path('api/comments/', include('CommentsApp.urls')),
    path('api/subscriptions/', users_views.MyUserSubscriptionsView.as_view()),
    path('api/subscriptions/articles/', articles_views.SubscribedArticlesView.as_view()),
    path('api/auth/', UserAuthToken.as_view()),
}
