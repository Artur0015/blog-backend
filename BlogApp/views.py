from rest_framework import viewsets, status
from rest_framework import generics
from .serializers import *
from .models import Article, Comment
from .paginators import ArticlePaginator
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .permissions import OwnerCanChangeAuthenticatedCanCreateOthersReadOnly, IsOwnerOrReadOnly
from rest_framework.exceptions import NotFound


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    pagination_class = ArticlePaginator
    queryset = Article.objects.select_related('author').all()
    permission_classes = [OwnerCanChangeAuthenticatedCanCreateOthersReadOnly]
    http_method_names = ["post", "put", "get", "options", "head", "delete"]

    def get_queryset(self):
        return self.queryset.order_by('-id')


class CommentsView(generics.ListCreateAPIView):
    queryset = Comment.objects.all().select_related('author').select_related('for_article')
    serializer_class = CommentSerializer
    permission_classes = [OwnerCanChangeAuthenticatedCanCreateOthersReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        article_id = kwargs.get('id')
        return Response(self.get_serializer(queryset.filter(for_article=article_id), many=True).data)


class UserRegistartion(generics.CreateAPIView):
    serializer_class = MyUserSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)


class UserLogin(viewsets.views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        if not serializer.validated_data['remember_me']:
            request.session.set_expiry(0)
        return Response(MyUserSerializer(user).data)

    def delete(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserInfo(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MyUserSerializer

    def get_object(self):
        return self.request.user


class UserProfile(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self):
        username = self.request.resolver_match.kwargs.get('username')
        try:
            user = User.objects.prefetch_related('article_set').get(username=username)
        except ObjectDoesNotExist:
            raise NotFound()
        return user


class UploadImage(generics.CreateAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    serializer_class = ImageUploadSerializer
