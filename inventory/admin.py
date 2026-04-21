from django.contrib import admin
from .models import StockRecord, StockMovement


@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ["product", "quantity_on_hand", "available", "needs_reorder"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["product", "movement_type", "quantity", "created_at"]
