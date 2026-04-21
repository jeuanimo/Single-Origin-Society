from django.contrib import admin
from .models import Order, OrderItem, Return


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "email", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order_number", "email", "last_name"]
    inlines = [OrderItemInline]


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ["return_number", "order", "reason", "status", "refund_amount", "created_at"]
    list_filter = ["status", "reason", "created_at"]
    search_fields = ["return_number", "order__order_number"]
    readonly_fields = ["return_number", "created_at", "updated_at"]
