from django.contrib import admin
from .models import Transaction, Expense


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["transaction_type", "description", "amount", "date"]
    list_filter = ["transaction_type", "date"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["description", "amount", "category", "date"]
    list_filter = ["category", "date"]
