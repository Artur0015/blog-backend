from django.db.models import Count
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Blog.api_views import UpdateWithoutMakingResponse, CreateWithoutMakingResponse
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
    queryset = User.objects.all().annotate(Count('articles__likes'), Count('articles__dislikes')) \
        .defer('articles__photo', 'articles__header', 'articles__pub_date', )


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
