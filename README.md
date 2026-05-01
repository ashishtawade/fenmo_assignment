# fenmo_assignment

Minimal full-stack expense tracker built with Django, server-rendered HTML, and basic JavaScript.

## Notes on the implementation

### Key design decisions

- I used Django with server-rendered HTML and a small amount of vanilla JavaScript. For this assignment, that felt like the simplest way to keep the stack easy to run while still separating backend and frontend responsibilities cleanly.
- The backend is split into thin views and service functions. The views in `expenses/views.py` handle HTTP concerns, while `expenses/services.py` contains the logic for creating and listing expenses. That keeps the code easier to extend and test.
- I used SQLite through the Django ORM for persistence. It is durable, works well for a small assignment, and does not require any external setup. It also gives transactional behavior, which is useful for handling idempotent create requests safely.
- Money is stored using `DecimalField` rather than floats, because even in a small expense tracker it is better to avoid floating-point issues for currency values.
- To handle retries and refreshes safely, the create endpoint expects an `Idempotency-Key`. I store that key with a hash of the request payload so the server can distinguish a real retry from a different request that accidentally reused the same key.

### Trade-offs made because of the timebox

- The UI is intentionally simple. I focused more on correctness, clear behavior, and resilience than on advanced styling or richer interactions.
- I kept the frontend in a single template with inline JavaScript instead of introducing a larger frontend structure. That keeps the assignment small and readable, though in a larger app I would likely split the JavaScript into separate files or use a frontend framework if the complexity justified it.
- The filtering and sorting needs for this assignment are small, so I kept them limited to category filtering and newest-first sorting by date instead of building a broader query system.
- The idempotency flow is implemented for the create-expense path only, since that is the place where retries matter most for this assignment.

### Things I intentionally did not do

- I did not add authentication or user accounts. The assignment reads like a single-user personal finance tool, so I kept the scope focused on expense tracking itself.
- I did not add edit/delete expense actions, pagination, category management, CSV export, or charts. Those would be reasonable next steps, but they were outside the requested feature set.
- I did not build a full API versioning strategy or introduce Django REST Framework, because the required API surface is small and standard Django is enough here.
- I did not add background jobs, optimistic UI updates, or offline-first sync. The app does handle retries and refreshes safely, but it stops short of being a full offline-capable experience.
- I did not commit the SQLite database file. The schema is created through migrations, and keeping the database out of git makes the repository cleaner.

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
