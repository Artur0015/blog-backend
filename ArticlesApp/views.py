from rest_framework import status
from rest_framework import generics
from rest_framework.generics import get_object_or_404, RetrieveDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Count
from rest_framework.views import APIView

from Blog.api_views import UpdateWithoutMakingResponse, CreateWithoutMakingResponse
from .models import Article
from Blog.pagination import PaginateWithRawQueryset
from Blog.permissions import IsOwnerOrReadOnly
from .paginators import ArticlePaginator

from .serializers import ArticleRetrieveSerializer, ArticleListSerializer, ArticleSerializerForProfile


class ArticleListCreateView(PaginateWithRawQueryset, CreateWithoutMakingResponse, ListAPIView):
    pagination_class = ArticlePaginator
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['post', 'patch', 'get', 'options', 'head', 'delete', 'put']
    serializer_class = ArticleListSerializer

    def create(self, request, *args, **kwargs):
        serializer = super().create(request, *args, **kwargs)
        return Response({'id': serializer.data.get('id')}, status.HTTP_201_CREATED)

    @property
    def raw_queryset(self):
        return Article.objects.all()

    def get_queryset(self):
        return self.raw_queryset.select_related('author').annotate(Count('likes'), Count('dislikes')) \
            .only('author__username', 'author__photo', 'id', 'header', 'pub_date', 'photo').order_by('-id')


class ArticleUpdateDestroyRetrieveView(UpdateWithoutMakingResponse, RetrieveDestroyAPIView):
    serializer_class = ArticleRetrieveSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Article.objects.all().only('id', 'author_id', 'author__id')
        if self.request.method == 'GET':
            queryset = Article.objects.all().select_related('author').annotate(Count('likes'), Count('dislikes')) \
                .only('author__username', 'author__photo', 'id', 'header', 'pub_date', 'photo', 'text').order_by('-id')
        return queryset

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_202_ACCEPTED)


class ArticleLikesDislikesView(APIView):
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


class UserArticlesView(PaginateWithRawQueryset, generics.ListAPIView):
    pagination_class = ArticlePaginator
    serializer_class = ArticleSerializerForProfile

    @property
    def raw_queryset(self):
        return Article.objects.filter(author__username=self.kwargs.get('username'))

    def get_queryset(self):
        return self.raw_queryset \
            .annotate(Count('likes'), Count('dislikes')).only('id', 'header', 'pub_date', 'photo').order_by('-id')


class SubscribedArticlesView(PaginateWithRawQueryset, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleListSerializer
    pagination_class = ArticlePaginator

    @property
    def raw_queryset(self):
        return Article.objects.filter(author__in=self.request.user.subscriptions.all())

    def get_queryset(self):
        return self.raw_queryset.select_related('author').annotate(Count('likes'), Count('dislikes')) \
            .only('author__id', 'author__username', 'author__photo', 'id', 'header', 'pub_date', 'photo', ) \
            .order_by('-id')
