from django.contrib import admin

from .models import Recipe, Favorite, Ingridient, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


@admin.register(Ingridient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    list_filter = ('name',)


admin.site.empty_value_display = 'Не задано'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author'
    )
    list_filter = (
        'name', 'author', 'tags'
    )
    readonly_fields = ('in_favorite_count',)

    def in_favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


admin.site.empty_value_display = 'Не задано'
