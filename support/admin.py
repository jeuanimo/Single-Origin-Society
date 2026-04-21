from django.contrib import admin
from .models import Ticket, TicketMessage


class TicketMessageInline(admin.StackedInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ("author", "is_staff_reply", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_number", "subject", "category", "priority", "status", "user", "assigned_to", "created_at")
    list_filter = ("status", "priority", "category", "created_at")
    search_fields = ("ticket_number", "subject", "email", "user__email")
    inlines = [TicketMessageInline]
    readonly_fields = ("ticket_number", "created_at", "updated_at")
