from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import (Ingredient, Recipe, Favorite,
                     ShoppingCart, IngredientInRecipe)
from .serializers import (IngredientSerializer,
                          RecipeListSerializer, RecipeCreateSerializer)
from .permissions import IsAuthorOrReadOnly
from .filters import IngredientSearchFilter, RecipeFilter
from users.serializers import RecipeMinifiedSerializer
from django.urls import reverse


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_link']:
            permission_classes = [AllowAny]
        elif self.action in ['favorite', 'shopping_cart',
                             'download_shopping_cart', 'create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthorOrReadOnly]
        return [permission() for permission in permission_classes]

    def recipe_redirect_short_link(request, recipe_pk):
        get_object_or_404(Recipe, pk=recipe_pk)
        return redirect(f"/recipes/{recipe_pk}/")

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    def _add_or_remove_from(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            # This part is correct
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже добавлен.'},
                                status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        instance = model.objects.filter(user=user, recipe=recipe)
        if instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Рецепт не был добавлен в этот список.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self._add_or_remove_from(Favorite, request, pk)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove_from(ShoppingCart, request, pk)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        shopping_list = "Список покупок для Foodgram:\n\n"
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total_amount']
            shopping_list += f"• {name} ({unit}) — {amount}\n"

        response = HttpResponse(
            shopping_list, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True, methods=["get"], url_path="get-link"
    )
    def get_link(self, request, pk=None):
        short_link_path = reverse(
            "recipe-short-link", args=[pk])
        absolute_short_link = request.build_absolute_uri(short_link_path)
        return Response({"short-link": absolute_short_link},
                        status=status.HTTP_200_OK)
