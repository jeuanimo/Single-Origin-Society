from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


class POItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_name", "email", "is_active"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["po_number", "supplier", "status", "total", "created_at"]
    inlines = [POItemInline]
