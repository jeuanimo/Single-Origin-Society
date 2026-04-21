from django.db import models
from django.conf import settings


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("confirmed", "Confirmed"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    ]
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="purchase_orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.po_number

    def calculate_total(self):
        self.total = sum(item.total_cost for item in self.items.all())
        self.save(update_fields=["total"])


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


class PurchaseOrderLine(PurchaseOrderItem):
    class Meta:
        proxy = True
        verbose_name = "purchase order line"
        verbose_name_plural = "purchase order lines"
