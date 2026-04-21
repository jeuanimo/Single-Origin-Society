from django.contrib import admin
from .models import Shipment, ShippingRate


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ["order", "carrier", "tracking_number", "status"]
    list_filter = ["status", "carrier"]


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ["name", "carrier", "rate", "is_active"]
