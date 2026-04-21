from django.conf import settings
from django.db import models


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_container"
    )
    name = models.CharField(max_length=120, default="My Wishlist")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.email} - {self.name}"


class WishlistItem(models.Model):
    """Products a customer has saved to their wishlist."""

    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items", null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist"
    )
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.email} — {self.product.name}"

    def save(self, *args, **kwargs):
        if self.user_id and not self.wishlist_id:
            self.wishlist, _ = Wishlist.objects.get_or_create(user=self.user)
        super().save(*args, **kwargs)


class CustomerNote(models.Model):
    """Internal notes about a customer for CRM purposes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_notes"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="authored_notes"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.user.email} — {self.created_at:%Y-%m-%d}"


class InternalNote(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="internal_notes_authored"
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="internal_notes"
    )
    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="internal_notes")
    support_ticket = models.ForeignKey("support.Ticket", on_delete=models.SET_NULL, null=True, blank=True, related_name="internal_notes")
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject or f"Internal note {self.pk}"
