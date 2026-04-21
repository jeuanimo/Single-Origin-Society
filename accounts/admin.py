from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "is_active", "date_joined"]
    list_filter = ["role", "is_active"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extra", {"fields": ("role", "phone", "company", "notes")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "label", "city", "state"]
