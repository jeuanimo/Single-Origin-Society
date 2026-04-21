from django.contrib import admin
from .models import CheckoutSession


@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "email", "created_at")
    list_filter = ("status", "created_at")
    readonly_fields = ("stripe_payment_intent", "stripe_client_secret", "created_at", "updated_at")
    search_fields = ("email", "stripe_payment_intent")
