from django.conf import settings
from django.db import models
from products.models import Product


class Cart(models.Model):
    """Persistent shopping cart — links to user or session."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
    )
    session_key = models.CharField(max_length=40, blank=True, default="", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        if self.user:
            return f"Cart — {self.user.email}"
        return f"Cart — session {self.session_key}"

    @property
    def total(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.quantity}× {self.product.name}"

    @property
    def line_total(self):
        return self.product.price * self.quantity
