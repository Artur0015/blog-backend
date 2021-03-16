from rest_framework import viewsets, status
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from .serializers import *
from .models import Article, Comment
from .paginators import ArticlePaginator, PaginateWithRawQueryset, ArticlePaginatorForProfile
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .permissions import OwnerCanChangeAuthenticatedCanCreateOthersReadOnly, IsOwnerOrReadOnly
from django.db.models import Count


class ArticleViewSet(PaginateWithRawQueryset, viewsets.ModelViewSet):
    pagination_class = ArticlePaginator
    permission_classes = [OwnerCanChangeAuthenticatedCanCreateOthersReadOnly]
    http_method_names = ["post", "patch", "get", "options", "head", "delete"]

    def get_serializer_class(self):
        if self.kwargs.get('pk'):
            return ArticleRetrieveSerializer
        return ArticleListSerializer

    @property
    def raw_queryset(self):
        return Article.objects.all()

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_202_ACCEPTED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data.get('id'), status.HTTP_201_CREATED)

    def get_queryset(self):
        only = ['author__username', 'id', 'header', 'pub_date']
        if self.kwargs.get('pk'):
            only.append('text')
        queryset = self.raw_queryset.select_related('author'). \
            order_by('-id').annotate(Count('likes'), Count('dislikes')).only(*only)
        return queryset


class CommentsView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [OwnerCanChangeAuthenticatedCanCreateOthersReadOnly]

    def get_queryset(self):
        return Comment.objects.select_related('author').filter(for_article__id=self.kwargs.get('pk')) \
            .only('author__id', 'author__username', 'author__photo', 'text')

    def get_serializer_context(self):
        return {
            'request': self.request,
            'article_id': self.kwargs.get('pk')
        }


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()


class ArticleLikesDislikesView(viewsets.views.APIView):
    permission_classes = [IsAuthenticated]

    def get_table(self, article):
        if self.field == 'likes':
            return [article.likes, article.dislikes]
        elif self.field == 'dislikes':
            return [article.dislikes, article.likes]

    def post(self, request, pk):
        article = get_object_or_404(Article.objects.all().only('id'), pk=pk)
        table = self.get_table(article)
        table[1].remove(request.user)
        table[0].add(request.user)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        article = get_object_or_404(Article.objects.all().only('id'), pk=pk)
        self.get_table(article)[0].remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArticleLikesView(ArticleLikesDislikesView):
    field = 'likes'


class ArticleDislikesView(ArticleLikesDislikesView):
    field = 'dislikes'


class UserRegistration(generics.CreateAPIView):
    serializer_class = UserSerializer

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
        return Response(UserSerializer(user).data)

    def delete(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserInfo(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch", "get", "options", "head"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserProfileSerializer

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_202_ACCEPTED)

    def get_object(self):
        return self.request.user


class UserProfile(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = User.objects.all().only('id', 'username', 'photo', 'about_me')
    lookup_field = 'username'


class UserArticles(PaginateWithRawQueryset, generics.ListAPIView):
    pagination_class = ArticlePaginatorForProfile
    serializer_class = ArticleSerializerForProfile

    @property
    def raw_queryset(self):
        return Article.objects.filter(author__username=self.kwargs.get('username'))

    def get_queryset(self):
        return self.raw_queryset \
            .annotate(Count('likes'), Count('dislikes'), count=Count('id')) \
            .only('id', 'header', 'pub_date').order_by('-id')


class UploadImage(generics.CreateAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    serializer_class = ImageUploadSerializer
