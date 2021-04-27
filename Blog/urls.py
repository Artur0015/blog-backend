from django.urls import include, path

from UsersApp.views import UserAuthToken

urlpatterns = [
    path('api/articles/', include('ArticlesApp.urls')),
    path('api/users/', include('UsersApp.urls')),
    path('api/comments/', include('CommentsApp.urls')),
    path('api/auth/', UserAuthToken.as_view())
]
