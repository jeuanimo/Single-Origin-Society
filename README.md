# Single Origin Society

> Quiet luxury for the intentional palate.

A Django 6.0 e-commerce platform for specialty single-origin coffee, featuring a customer storefront, internal management portal, Stripe payments, CRM, fundraising, and full inventory/order management.

---

## Quick Start (local)

```bash
# 1. Clone & enter
cd "Single Origin Society"

# 2. Create virtualenv & install deps
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Set up env vars
cp .env.example .env
# Edit .env with your secrets

# 4. Migrate & create superuser
python manage.py migrate
python manage.py createsuperuser

# 5. Run dev server
python manage.py runserver
```

## Quick Start (Docker)

```bash
cp .env.example .env   # edit values first
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Apps

| App | Purpose |
|---|---|
| accounts | Custom user model, auth, addresses |
| products | Catalogue, tasting notes, brewing guides |
| orders | Order management, line items |
| inventory | Stock records & movements |
| purchasing | Suppliers, purchase orders |
| crm | Customer profiles, tiers, interactions |
| marketing | Campaigns, coupons, email subscribers |
| content | Pages, blog posts, ritual journal |
| fundraising | Campaigns & donations |
| finance | Transactions & expenses |
| reporting | Daily summary snapshots |
| shipping | Shipments & shipping rates |
| cart | Shopping-cart models & session management |
| checkout | Stripe checkout flow, webhook handling |
| customers | Wishlists, customer notes |
| support | Support ticket system |
| reviews | Product reviews with moderation |
| business_config | Singleton store-wide settings |
| portal | Staff management dashboard |
| storefront | Public-facing shop |

## Tech Stack

- **Django 6.0** · Python 3.12
- **PostgreSQL 16** (SQLite for local dev)
- **Stripe** for payments
- **django-htmx** for progressive enhancement
- **Custom CSS** design system (no Bootstrap/Tailwind)
- **Google Fonts** – Playfair Display + Inter
- **Docker** + **Gunicorn** for production
