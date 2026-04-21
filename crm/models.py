from django.db import models
from django.conf import settings


class CustomerTag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CustomerProfile(models.Model):
    TIER_CHOICES = [
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crm_profile")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="bronze")
    lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    last_order_date = models.DateTimeField(null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    tag_objects = models.ManyToManyField(CustomerTag, blank=True, related_name="customer_profiles")
    notes = models.TextField(blank=True)
    subscribed_email = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.tier})"


class Interaction(models.Model):
    TYPE_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone"),
        ("chat", "Chat"),
        ("note", "Internal Note"),
        ("order", "Order"),
        ("return", "Return"),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interactions")
    interaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_interactions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.interaction_type}: {self.subject}"
