from django.db import models
from django.conf import settings


class StockRecord(models.Model):
    product = models.OneToOneField("products.Product", on_delete=models.CASCADE, related_name="stock")
    quantity_on_hand = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    reorder_quantity = models.IntegerField(default=50)
    location = models.CharField(max_length=100, blank=True)
    last_counted = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available(self):
        return self.quantity_on_hand - self.quantity_reserved

    @property
    def needs_reorder(self):
        return self.available <= self.reorder_level

    def __str__(self):
        return f"{self.product.name}: {self.available} available"


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ("in", "Stock In"),
        ("out", "Stock Out"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
    ]
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.movement_type}: {self.product.name} ({self.quantity})"


class InventoryItem(StockRecord):
    class Meta:
        proxy = True
        verbose_name = "inventory item"
        verbose_name_plural = "inventory items"


class InventoryAdjustment(StockMovement):
    class Meta:
        proxy = True
        verbose_name = "inventory adjustment"
        verbose_name_plural = "inventory adjustments"
