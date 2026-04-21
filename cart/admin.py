from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "added_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "item_count", "total", "updated_at")
    list_filter = ("updated_at",)
    inlines = [CartItemInline]
    readonly_fields = ("user", "session_key", "created_at", "updated_at")
