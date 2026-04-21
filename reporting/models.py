from django.db import models
from django.conf import settings


class DailySummary(models.Model):
    date = models.DateField(unique=True)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_customers = models.IntegerField(default=0)
    items_sold = models.IntegerField(default=0)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    top_product = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = "daily summaries"
        ordering = ["-date"]

    def __str__(self):
        return f"Summary: {self.date}"


class ActivityLog(models.Model):
    """Central audit log for all staff actions across the portal."""

    ACTION_CHOICES = [
        ("create", "Created"),
        ("update", "Updated"),
        ("delete", "Deleted"),
        ("status_change", "Status Changed"),
        ("note", "Note Added"),
        ("login", "Logged In"),
        ("export", "Exported"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="activity_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    entity_label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "activity log"
        verbose_name_plural = "activity logs"

    def __str__(self):
        return f"{self.user} — {self.get_action_display()} {self.entity_type} {self.entity_label}"


class DashboardMetricSnapshot(DailySummary):
    class Meta:
        proxy = True
        verbose_name = "dashboard metric snapshot"
        verbose_name_plural = "dashboard metric snapshots"
