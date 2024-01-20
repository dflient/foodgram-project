from django.contrib import admin

from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author'
    )
    list_filter = (
        'name', 'author', 'tags'
    )
    readonly_fields = ('in_favorite_count',)


admin.site.empty_value_display = 'Не задано'
