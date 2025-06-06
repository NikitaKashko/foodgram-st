from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path(
        'users/me/avatar/',
        CustomUserViewSet.as_view({'put': 'avatar', 'delete': 'avatar'}),
        name='user-avatar'
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
