from django.contrib import admin
from .models import DailySummary, ActivityLog


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ["date", "total_orders", "total_revenue", "new_customers"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "entity_type", "entity_label", "created_at"]
    list_filter = ["action", "entity_type", "created_at"]
    search_fields = ["entity_label", "description", "user__email"]
    readonly_fields = ["user", "action", "entity_type", "entity_id", "entity_label", "description", "ip_address", "created_at"]
