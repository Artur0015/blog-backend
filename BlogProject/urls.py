from django.urls import include, path

urlpatterns = [
    path('api/articles/', include('ArticlesApp.urls')),
    path('api/users/', include('UsersApp.urls')),
    path('api/comments/', include('CommentsApp.urls')),
]
