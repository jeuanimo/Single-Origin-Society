from django.db import models
from django.conf import settings


class Shipment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("label_created", "Label Created"),
        ("picked_up", "Picked Up"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("exception", "Exception"),
    ]
    CARRIER_CHOICES = [
        ("usps", "USPS"),
        ("ups", "UPS"),
        ("fedex", "FedEx"),
        ("dhl", "DHL"),
        ("other", "Other"),
    ]
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="shipments")
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES, default="usps")
    tracking_number = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Shipment for {self.order.order_number}"


class ShippingRate(models.Model):
    name = models.CharField(max_length=100)
    carrier = models.CharField(max_length=20)
    min_weight = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_weight = models.DecimalField(max_digits=6, decimal_places=2)
    rate = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_days = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}: ${self.rate}"
