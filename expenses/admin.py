from django.contrib import admin

from .models import Expense, ExpenseRequest


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "category", "description", "date", "created_at")
    search_fields = ("category", "description")
    list_filter = ("category", "date")


@admin.register(ExpenseRequest)
class ExpenseRequestAdmin(admin.ModelAdmin):
    list_display = ("idempotency_key", "request_hash", "expense", "created_at")
    search_fields = ("idempotency_key", "request_hash")
