from django.contrib import admin

from .models import Ingridient


@admin.register(Ingridient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    list_filter = ('name',)


admin.site.empty_value_display = 'Не задано'
