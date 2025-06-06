from django.contrib import admin
from .models import (Ingredient, Recipe,
                     IngredientInRecipe, Favorite, ShoppingCart)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited_count')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name')
    inlines = (IngredientInRecipeInline,)

    def favorited_count(self, obj):
        return obj.favorited_by.count()
    favorited_count.short_description = 'Число добавлений в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
