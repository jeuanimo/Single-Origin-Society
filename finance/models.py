from django.db import models
from django.conf import settings


class Transaction(models.Model):
    TYPE_CHOICES = [
        ("sale", "Sale"),
        ("refund", "Refund"),
        ("expense", "Expense"),
        ("payout", "Payout"),
        ("donation", "Donation"),
    ]
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=300)
    reference = models.CharField(max_length=200, blank=True)
    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.transaction_type}: {self.description} (${self.amount})"


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("cogs", "Cost of Goods"),
        ("shipping", "Shipping"),
        ("marketing", "Marketing"),
        ("operations", "Operations"),
        ("payroll", "Payroll"),
        ("rent", "Rent"),
        ("utilities", "Utilities"),
        ("software", "Software"),
        ("other", "Other"),
    ]
    description = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    vendor = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    receipt = models.FileField(upload_to="receipts/", blank=True)
    notes = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.description}: ${self.amount}"


class BusinessExpense(Expense):
    class Meta:
        proxy = True
        verbose_name = "business expense"
        verbose_name_plural = "business expenses"
