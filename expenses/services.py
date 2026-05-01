import hashlib
import json

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Sum

from .forms import validate_expense_payload
from .models import Expense, ExpenseRequest


def _build_request_hash(cleaned_payload):
    serialized = json.dumps(
        {
            "amount": str(cleaned_payload["amount"]),
            "category": cleaned_payload["category"],
            "description": cleaned_payload["description"],
            "date": cleaned_payload["date"].isoformat(),
        },
        sort_keys=True,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def serialize_expense(expense):
    return {
        "id": expense.id,
        "amount": f"{expense.amount:.2f}",
        "category": expense.category,
        "description": expense.description,
        "date": expense.date.isoformat(),
        "created_at": expense.created_at.isoformat(),
    }


def create_expense(payload, idempotency_key):
    if not idempotency_key:
        raise ValidationError({"idempotency_key": "Idempotency-Key header is required."})

    cleaned_payload = validate_expense_payload(payload)
    request_hash = _build_request_hash(cleaned_payload)

    try:
        with transaction.atomic():
            request_record = ExpenseRequest.objects.select_for_update().filter(
                idempotency_key=idempotency_key
            ).first()

            if request_record:
                if request_record.request_hash != request_hash:
                    raise ValidationError(
                        {
                            "idempotency_key": (
                                "This Idempotency-Key was already used for a different request."
                            )
                        }
                    )
                if request_record.expense_id:
                    return request_record.expense, False

            expense = Expense.objects.create(**cleaned_payload)

            if request_record:
                request_record.request_hash = request_hash
                request_record.expense = expense
                request_record.save(update_fields=["request_hash", "expense"])
            else:
                ExpenseRequest.objects.create(
                    idempotency_key=idempotency_key,
                    request_hash=request_hash,
                    expense=expense,
                )
    except IntegrityError:
        existing = ExpenseRequest.objects.select_related("expense").get(
            idempotency_key=idempotency_key
        )
        if existing.request_hash != request_hash:
            raise ValidationError(
                {
                    "idempotency_key": (
                        "This Idempotency-Key was already used for a different request."
                    )
                }
            )
        return existing.expense, False

    return expense, True


def list_expenses(*, category=None, sort=None):
    queryset = Expense.objects.all()

    if category:
        queryset = queryset.filter(category__iexact=category.strip())

    if sort == "date_desc":
        queryset = queryset.order_by("-date", "-created_at", "-id")

    expenses = list(queryset)
    total = queryset.aggregate(total=Sum("amount"))["total"] or 0
    categories = list(
        Expense.objects.order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )

    return {
        "expenses": [serialize_expense(expense) for expense in expenses],
        "total": f"{total:.2f}",
        "categories": categories,
    }
