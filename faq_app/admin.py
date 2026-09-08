from django.contrib import admin
from .models import FAQ, FAQCategory


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1
    fields = ("question", "order", "is_active")


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    inlines = [FAQInline]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "order", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("question", "answer")
    ordering = ("category__order", "order")
