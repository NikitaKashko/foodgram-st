from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет редактировать объект только его автору.
    Для чтения доступно всем.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение разрешены для любого запроса,
        # поэтому мы всегда будем разрешать GET, HEAD или OPTIONS запросы.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешения на запись предоставляются только автору объекта.
        return obj.author == request.user
