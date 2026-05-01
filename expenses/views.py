import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .services import create_expense, list_expenses


@ensure_csrf_cookie
def index(request):
    return render(request, "expenses/index.html")


@require_http_methods(["GET", "POST"])
def expenses_collection(request):
    if request.method == "GET":
        data = list_expenses(
            category=request.GET.get("category"),
            sort=request.GET.get("sort"),
        )
        return JsonResponse(data)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"errors": {"body": "Request body must be valid JSON."}}, status=400)

    try:
        expense, created = create_expense(
            payload,
            request.headers.get("Idempotency-Key"),
        )
    except ValidationError as exc:
        return JsonResponse({"errors": exc.message_dict}, status=400)

    return JsonResponse(
        {
            "expense": {
                "id": expense.id,
                "amount": f"{expense.amount:.2f}",
                "category": expense.category,
                "description": expense.description,
                "date": expense.date.isoformat(),
                "created_at": expense.created_at.isoformat(),
            }
        },
        status=201 if created else 200,
    )
