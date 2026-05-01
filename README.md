# fenmo_assignment

Minimal full-stack expense tracker built with Django, server-rendered HTML, and basic JavaScript.

## Tech choices

- Backend: Django with thin views and service-layer functions in `expenses/services.py`.
- Persistence: SQLite via Django ORM.
  SQLite is a good fit here because it is durable, requires no separate service to run the assignment, and still gives us transactional behavior for idempotent request handling.
- Frontend: a single Django template with basic JavaScript and CSS.

## Features

- Create an expense with amount, category, description, and date
- List expenses
- Filter expenses by category
- Sort expenses by date descending
- Show the total for the current filtered list
- Retry-safe expense creation with an `Idempotency-Key` header

## API

### `POST /expenses`

Creates a new expense.

Headers:

- `Content-Type: application/json`
- `Idempotency-Key: <unique-key>`

Example body:

```json
{
  "amount": "245.50",
  "category": "Food",
  "description": "Lunch with team",
  "date": "2026-05-01"
}
```

Behavior:

- First successful request returns `201 Created`
- A retry with the same `Idempotency-Key` and same payload returns the original expense with `200 OK`
- Reusing the same `Idempotency-Key` for a different payload returns `400 Bad Request`

### `GET /expenses`

Returns expenses and summary metadata.

Optional query params:

- `category=<value>`
- `sort=date_desc`

Example response:

```json
{
  "expenses": [
    {
      "id": 1,
      "amount": "245.50",
      "category": "Food",
      "description": "Lunch with team",
      "date": "2026-05-01",
      "created_at": "2026-05-01T10:30:00+05:30"
    }
  ],
  "total": "245.50",
  "categories": ["Food"]
}
```

## Local setup

1. Create or activate a Python environment with Django available.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start the app:

```bash
python manage.py runserver
```

5. Open `http://127.0.0.1:8000/`

## Project structure

- `expenses/views.py`: HTTP layer only
- `expenses/services.py`: business logic for create/list behavior
- `expenses/forms.py`: payload validation
- `expenses/models.py`: persistence models
- `templates/expenses/index.html`: simple UI
