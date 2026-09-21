# Pharmacy Inventory System

A Django and Django REST Framework backend for managing medicines, suppliers, inventory batches, purchases, stock movements, and pharmacy operations.

## Features

- Medicine catalog with categories and manufacturers
- Supplier management
- Batch-level inventory tracking
- Stock transactions and stock adjustments
- Purchase processing with automatic inventory updates
- Role-aware permissions for pharmacy users
- UUID-based records for core business entities
- Filtering, searching, ordering, and pagination through Django REST Framework
- PostgreSQL database support

## Technology Stack

- Python 3.11+
- Django 5.2+
- Django REST Framework
- django-filter
- django-cors-headers
- PostgreSQL

## Project Structure

```text
pharmacy_backend/
├── apps/
│   ├── accounts/       # User profiles, roles, and permissions
│   ├── customers/      # Customer domain models
│   ├── inventory/      # Batches, stock, and stock transactions
│   ├── medicines/      # Medicines, categories, and manufacturers
│   ├── purchases/      # Purchases and purchase items
│   ├── sales/          # Sales domain services and views
│   └── suppliers/      # Supplier records
├── config/             # Django settings, URL configuration, ASGI, and WSGI
├── manage.py
└── README.md
```

## Prerequisites

- Python 3.11 or newer
- PostgreSQL 13 or newer
- Git

## Local Setup

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/su-ip/Pharmacy_inventory_system.git
   cd Pharmacy_inventory_system
   ```

2. Create and activate a virtual environment:

   **Windows PowerShell:**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the project dependencies:

   ```bash
   pip install django djangorestframework django-filter django-cors-headers psycopg[binary]
   ```

4. Create a PostgreSQL database and configure the connection in `config/settings.py` for local development. Do not commit passwords or production secrets to source control.

5. Apply migrations:

   ```bash
   python manage.py migrate
   ```

6. Create an administrator account:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

The API is available at `http://127.0.0.1:8000/` and the Django admin is available at `http://127.0.0.1:8000/admin/`.

## API Endpoints

All API endpoints require authentication unless explicitly configured otherwise.

### Medicines

| Resource | Endpoint |
| --- | --- |
| Categories | `GET/POST /api/categories/` |
| Manufacturers | `GET/POST /api/manufacturers/` |
| Medicines | `GET/POST /api/medicines/` |

Django REST Framework router actions such as detail, update, and delete are available for these resources.

### Inventory

| Resource | Endpoint |
| --- | --- |
| Batches | `GET/POST /api/inventory/batches/` |
| Stock transactions | `GET /api/inventory/stock-transactions/` |
| Stock adjustment | `POST /api/inventory/stock/adjust/` |

### Purchases

| Resource | Endpoint |
| --- | --- |
| Purchases | `GET/POST /api/purchases/` |

Creating a purchase validates the supplier and medicine references, creates or updates the batch, increases stock, records a stock transaction, and calculates the purchase total atomically.

Example purchase request:

```json
{
  "supplier": "supplier-uuid",
  "invoice_number": "INV-001",
  "purchase_date": "2026-09-21",
  "items": [
    {
      "medicine": "medicine-uuid",
      "batch_number": "BATCH-001",
      "manufacturing_date": "2026-01-01",
      "expiry_date": "2028-01-01",
      "quantity": 100,
      "purchase_price": "50.00",
      "selling_price": "65.00",
      "mrp": "70.00"
    }
  ],
  "discount": "0.00",
  "tax": "0.00"
}
```

## Authentication

The current API uses Django REST Framework session authentication and requires an authenticated user. Create a superuser with `createsuperuser`, or create users through the Django admin and assign the appropriate profile role.

Supported profile roles include:

- Admin
- Pharmacist
- Cashier
- Storekeeper

## Development Commands

```bash
# Validate the Django project
python manage.py check

# Create migrations after model changes
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Run tests
python manage.py test

# Start the development server
python manage.py runserver
```

## Configuration Notes

- Keep `SECRET_KEY`, database passwords, and other deployment credentials outside version control.
- Set `DEBUG = False` and configure `ALLOWED_HOSTS` for production.
- Replace `CORS_ALLOW_ALL_ORIGINS = True` with an explicit allowlist before production deployment.
- Use a production WSGI or ASGI server and serve static files through a production-ready setup.

## Repository

[GitHub: su-ip/Pharmacy_inventory_system](https://github.com/su-ip/Pharmacy_inventory_system)
