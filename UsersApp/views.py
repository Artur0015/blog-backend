from django.contrib.auth import logout, login
from django.db.models import Count
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from BlogProject.api_views import UpdateWithoutMakingResponse, CreateWithoutMakingResponse
from .models import User
from .serializers import UserSerializer, LoginSerializer, UserCreateSerializer, UserPartialSerializer


class UserRegistration(CreateWithoutMakingResponse):
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        if not request.data.get('remember_me'):
            request.session.set_expiry(0)
        return Response(UserPartialSerializer(user).data)

    def delete(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
