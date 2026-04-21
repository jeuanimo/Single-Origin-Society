from django.contrib import admin
from .models import WishlistItem, CustomerNote


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "added_at")
    list_filter = ("added_at",)
    search_fields = ("user__email", "product__name")


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ("user", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "body")
