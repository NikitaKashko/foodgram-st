from djoser.views import UserViewSet
from rest_framework import status, parsers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import User, Subscription
from .serializers import (
    CustomUserSerializer, SubscriptionSerializer, AvatarSerializer,
    SetAvatarSerializer
)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    parser_classes = [parsers.MultiPartParser,
                      parsers.JSONParser, parsers.FormParser]

    def get_permissions(self):
        if self.action == 'retrieve':
            return [AllowAny()]
        return super().get_permissions()

    @action(
        methods=["put", "delete"],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=SetAvatarSerializer,
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = SetAvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = AvatarSerializer(
            user, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user

        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            # This part is correct
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Subscription.objects.create(
                user=user, author=author)
            serializer = SubscriptionSerializer(
                subscription.author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE method - The logic is changed here
        subscription = Subscription.objects.filter(user=user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Вы не были подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

    @action(
        ["get", "put", "patch", "delete"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)
