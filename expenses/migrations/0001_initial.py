from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("category", models.CharField(max_length=100)),
                ("description", models.CharField(max_length=255)),
                ("date", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-date", "-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ExpenseRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("idempotency_key", models.CharField(max_length=255, unique=True)),
                ("request_hash", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "expense",
                    models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, related_name="request_records", to="expenses.expense"),
                ),
            ],
        ),
    ]
