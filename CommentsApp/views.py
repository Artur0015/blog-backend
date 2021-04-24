from rest_framework import status
from rest_framework.generics import DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from BlogProject.api_views import UpdateWithoutMakingResponse, CreateWithoutMakingResponse
from BlogProject.permissions import IsOwnerOrReadOnly
from .models import Comment
from .serializers import CommentSerializer


class CommentsDeleteUpdateView(UpdateWithoutMakingResponse, DestroyAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.all().select_related('author').only('id', 'author_id', 'author__id')

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_202_ACCEPTED)


class CommentsListCreateView(CreateWithoutMakingResponse, ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.all().select_related('author').only('id', 'author_id', 'author__id').filter(
            for_article__id=self.kwargs.get('pk')) \
            .only('author__id', 'author__username', 'author__photo', 'text', 'pub_date')

    def get_serializer_context(self):
        return {
            'request': self.request,
            'article_id': self.kwargs.get('pk')
        }

    def create(self, request, *args, **kwargs):
        serializer = super().create(request, *args, **kwargs)
        return Response({'id': serializer.data.get('id')}, status=status.HTTP_201_CREATED)
