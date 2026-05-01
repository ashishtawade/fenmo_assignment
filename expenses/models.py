from django.db import models


class Expense(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at", "-id"]

    def __str__(self):
        return f"{self.category}: {self.amount} on {self.date}"


class ExpenseRequest(models.Model):
    idempotency_key = models.CharField(max_length=255, unique=True)
    request_hash = models.CharField(max_length=64)
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="request_records",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.idempotency_key
