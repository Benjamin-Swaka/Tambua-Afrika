from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'is_digital',
        'created_at',
    )
    list_filter = ('category', 'is_digital')
    search_fields = ('name',)
