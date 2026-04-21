import uuid
from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    shipping_line1 = models.CharField(max_length=255)
    shipping_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default="US")
    SHIPPING_METHOD_CHOICES = [
        ("standard", "Standard"),
        ("express", "Express"),
        ("overnight", "Overnight"),
    ]
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHOD_CHOICES, default="standard")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    promo_code = models.CharField(max_length=50, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    gift_note = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SOS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Return(models.Model):
    """Tracks product returns and refund requests."""

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("received", "Item Received"),
        ("refunded", "Refunded"),
        ("denied", "Denied"),
    ]
    REASON_CHOICES = [
        ("defective", "Defective Product"),
        ("wrong_item", "Wrong Item Received"),
        ("not_as_described", "Not As Described"),
        ("changed_mind", "Changed Mind"),
        ("damaged", "Damaged in Shipping"),
        ("other", "Other"),
    ]

    return_number = models.CharField(max_length=32, unique=True, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="returns")
    item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="returns")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    description = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    resolution_notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_returns"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.return_number} — {self.order.order_number}"

    def save(self, *args, **kwargs):
        if not self.return_number:
            import uuid
            self.return_number = f"RET-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Payment(models.Model):
    PROVIDER_CHOICES = [
        ("stripe", "Stripe"),
        ("paypal", "PayPal"),
        ("manual", "Manual"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("authorized", "Authorized"),
        ("captured", "Captured"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("partially_refunded", "Partially Refunded"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="stripe")
    provider_payment_id = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=60, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.order_number} {self.provider} {self.status}"


class Refund(models.Model):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name="refunds")
    return_request = models.ForeignKey(Return, on_delete=models.SET_NULL, null=True, blank=True, related_name="refund_records")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    provider_refund_id = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_refunds"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund {self.order.order_number} ${self.amount}"
