from django.contrib import admin
from .models import CustomerProfile, Interaction


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "tier", "lifetime_value", "total_orders"]


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ["customer", "interaction_type", "subject", "created_at"]
