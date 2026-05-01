from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date


def validate_expense_payload(payload):
    errors = {}

    amount_raw = payload.get("amount")
    category = (payload.get("category") or "").strip()
    description = (payload.get("description") or "").strip()
    date_raw = payload.get("date")

    try:
        amount = Decimal(str(amount_raw))
        if amount <= 0:
            errors["amount"] = "Amount must be greater than 0."
        else:
            amount = amount.quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        errors["amount"] = "Amount must be a valid number."
        amount = None

    if not category:
        errors["category"] = "Category is required."

    if not description:
        errors["description"] = "Description is required."
    elif len(description) > 255:
        errors["description"] = "Description must be 255 characters or fewer."

    parsed_date = parse_date(date_raw or "")
    if parsed_date is None:
        errors["date"] = "Date must be a valid ISO date (YYYY-MM-DD)."

    if errors:
        raise ValidationError(errors)

    return {
        "amount": amount,
        "category": category,
        "description": description,
        "date": parsed_date,
    }
