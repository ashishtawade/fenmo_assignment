import json

from django.test import Client, TestCase
from django.urls import reverse

from .models import Expense


class ExpenseApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("expenses-collection")

    def test_creates_expense(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                "amount": "199.99",
                "category": "Food",
                "description": "Lunch",
                "date": "2026-05-01",
            }),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="expense-create-1",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(response.json()["expense"]["category"], "Food")

    def test_retry_with_same_idempotency_key_returns_original_expense(self):
        payload = {
            "amount": "199.99",
            "category": "Food",
            "description": "Lunch",
            "date": "2026-05-01",
        }

        first_response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="expense-create-2",
        )
        second_response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="expense-create-2",
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(
            first_response.json()["expense"]["id"],
            second_response.json()["expense"]["id"],
        )

    def test_reusing_same_idempotency_key_for_different_payload_fails(self):
        self.client.post(
            self.url,
            data=json.dumps({
                "amount": "199.99",
                "category": "Food",
                "description": "Lunch",
                "date": "2026-05-01",
            }),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="expense-create-3",
        )

        response = self.client.post(
            self.url,
            data=json.dumps({
                "amount": "49.99",
                "category": "Travel",
                "description": "Taxi",
                "date": "2026-05-02",
            }),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="expense-create-3",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Expense.objects.count(), 1)

    def test_lists_filtered_sorted_expenses_with_total(self):
        Expense.objects.create(
            amount="100.00",
            category="Food",
            description="Breakfast",
            date="2026-05-01",
        )
        Expense.objects.create(
            amount="60.00",
            category="Travel",
            description="Bus",
            date="2026-04-29",
        )
        Expense.objects.create(
            amount="250.00",
            category="Food",
            description="Dinner",
            date="2026-05-03",
        )

        response = self.client.get(self.url, {"category": "Food", "sort": "date_desc"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], "350.00")
        self.assertEqual(len(data["expenses"]), 2)
        self.assertEqual(data["expenses"][0]["description"], "Dinner")
        self.assertEqual(data["expenses"][1]["description"], "Breakfast")
