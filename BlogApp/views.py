from rest_framework import viewsets, status
from rest_framework import generics
from .serializers import *
from .models import Article, Comment, MyUser
from .paginators import ArticlePaginator
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .utils import OwnerCanChangeAuthenticatedCanCreateOthersReadOnly


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    pagination_class = ArticlePaginator
    queryset = Article.objects.select_related('author').all()
    permission_classes = [OwnerCanChangeAuthenticatedCanCreateOthersReadOnly]
    http_method_names = ['post', 'put', "get", "options", "head"]

    def get_queryset(self):
        return self.queryset.order_by('-id')


class CommentsView(generics.ListCreateAPIView):
    queryset = Comment.objects.all().select_related('author').select_related('for_article')
    serializer_class = CommentSerializer
    permission_classes = [OwnerCanChangeAuthenticatedCanCreateOthersReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        article_id = kwargs.get('pk')
        return Response(self.get_serializer(queryset.filter(for_article=article_id), many=True).data)

    def create(self, request, *args, **kwargs):
        article_id = kwargs.get('pk')
        serializer = self.get_serializer(context={'article_id': article_id, 'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class UserRegistartion(generics.CreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'OK'}, status.HTTP_201_CREATED)


class UserLogin(viewsets.views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        if not serializer.validated_data['remember_me']:
            request.session.set_expiry(0)
        my_user = MyUser.objects.get(user=user)
        return Response(UserSerializer(my_user).data)

    def delete(self, request):
        logout(request)
        return Response({'detail': 'OK'})


class UserInfo(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


    def get_object(self):
        user = self.request.user
        return MyUser.objects.get(user=user)


class UploadImage(generics.CreateAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    serializer_class = ImageUploadSerializer