from django.conf import settings
from django.db import models
import uuid


class Ticket(models.Model):
    """Customer support ticket."""

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("waiting", "Waiting on Customer"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]
    CATEGORY_CHOICES = [
        ("order", "Order Issue"),
        ("product", "Product Question"),
        ("shipping", "Shipping"),
        ("return", "Return / Refund"),
        ("account", "Account"),
        ("general", "General Inquiry"),
    ]

    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets"
    )
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="general")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    order = models.ForeignKey(
        "orders.Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_number} — {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class TicketMessage(models.Model):
    """A message within a support ticket thread."""

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="ticket_messages"
    )
    body = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    attachment = models.FileField(upload_to="support/attachments/%Y/%m/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message on {self.ticket.ticket_number} — {self.created_at:%Y-%m-%d %H:%M}"


class SupportTicket(Ticket):
    class Meta:
        proxy = True
        verbose_name = "support ticket"
        verbose_name_plural = "support tickets"
