from django.db.models import Count
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import RetrieveAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Blog.api_views import UpdateWithoutMakingResponse, CreateWithoutMakingResponse
from Blog.permissions import NotOwner
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, UserPartialSerializer


class UserRegistration(CreateWithoutMakingResponse):
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)


class UserInfoView(RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = 'username'
    queryset = User.objects.annotate(Count('articles__likes', distinct=True),
                                     Count('articles__dislikes', distinct=True), Count('subscribers', distinct=True))


class UserSubscribersView(APIView):
    permission_classes = [IsAuthenticated, NotOwner]

    def post(self, request, username):
        user = get_object_or_404(User.objects.all().only('id'), username=username)
        self.check_object_permissions(request, user)
        user.subscribers.add(request.user)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, username):
        user = get_object_or_404(User.objects.all().only('id'), username=username)
        request.user.subscriptions.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyUserSubscriptionsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPartialSerializer

    def get_queryset(self):
        return self.request.user.subscriptions.only('id', 'photo', 'username', )


class MyUserView(UpdateWithoutMakingResponse, RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPartialSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer_data = super().update(request, *args, **kwargs).data
        if request.data.get('photo'):
            return Response({'photo': serializer_data.get('photo')}, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_202_ACCEPTED)


class UserAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserPartialSerializer(user).data})
