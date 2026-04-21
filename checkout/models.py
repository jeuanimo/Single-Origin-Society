from django.db import models
from orders.models import Order


class CheckoutSession(models.Model):
    """Tracks an in-progress checkout before payment completes."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("abandoned", "Abandoned"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True, related_name="checkout_session")
    session_key = models.CharField(max_length=40, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    stripe_payment_intent = models.CharField(max_length=255, blank=True, default="")
    stripe_client_secret = models.CharField(max_length=255, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    shipping_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Checkout {self.pk} — {self.status}"
