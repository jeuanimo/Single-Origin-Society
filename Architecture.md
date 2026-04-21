# Single Origin Society Architecture Handoff

## 1) Full Django project structure

- accounts
- products
- orders
- inventory
- purchasing
- crm
- marketing
- content
- fundraising
- finance
- reporting
- shipping
- portal
- storefront
- cart
- checkout
- customers
- support
- reviews
- business_config
- sos_project
- templates
- static
- media
- services (new service-layer package)

## 2) App-by-app architecture explanation

- accounts: custom user model, addresses, role/permission policy.
- products: categories, products, variants, tasting notes, brewing guides.
- orders: order lifecycle, returns, payment and refund records.
- inventory: stock records and movements.
- purchasing: suppliers, purchase orders, PO line items.
- shipping: shipment records and rate table.
- crm: customer profile, tags, interactions.
- support: tickets and threaded messages.
- marketing: campaigns, coupons, subscribers, campaign landing pages, homepage promo blocks.
- content: pages, blog posts, inquiries (wholesale + ambassador) and internal inquiry notes.
- storefront: public catalog and content pages, checkout UX, newsletter and inquiry entry points.
- portal: internal operations UI and workflows.
- reporting: daily rollups and activity logs.
- services: domain service modules, typed DTO serializer modules, background worker utilities.

## 3) Database schema and model relationships

Core relationships:

- User -> Address (1:N)
- User -> Order (1:N, nullable for guests)
- Order -> OrderItem (1:N)
- Order -> Return (1:N)
- Order -> Shipment (1:N)
- Order -> Payment (1:N)
- Payment -> Refund (1:N)
- Category -> Product (1:N)
- Product -> ProductVariant (1:N)
- Product -> ProductImage (1:N)
- Product -> TastingNote (1:N)
- Product -> BrewingGuide (1:N, nullable)
- Product -> StockRecord (1:1)
- Product -> StockMovement (1:N)
- Supplier -> PurchaseOrder (1:N)
- PurchaseOrder -> PurchaseOrderItem (1:N)
- CustomerProfile <-> CustomerTag (M:N)
- Ticket -> TicketMessage (1:N)
- Campaign -> CampaignLandingPage (1:N)
- WholesaleInquiry -> WholesaleInquiryNote (1:N)
- AmbassadorInquiry -> AmbassadorInquiryNote (1:N)

## 4) URL architecture

- Root URLConf mounts app URLConfs by area.
- Public endpoints primarily under storefront + accounts + support/customers/reviews.
- Internal business portal under portal namespace.
- Payment webhook isolated under checkout webhook endpoint.

## 5) Views and template structure

- Public storefront templates in templates/storefront.
- Internal portal templates in templates/portal with module folders.
- Shared includes in templates/includes.
- Base shells:
  - storefront/base.html
  - portal/base.html

## 6) Forms and validation plan

Current state:

- Added portal forms for inquiry filter/action and product CSV import.
- Added content model forms for inquiry capture.

Validation approach:

- Use Django forms for all POST entry points.
- Parse filters and actions via typed serializer helpers.
- Preserve business rules in service layer + model constraints.

## 7) Role/permission system

- Role constants and permission matrix live in accounts.models.
- Route-level checks are centralized in accounts.decorators via portal view-name mapping.
- Template-level visibility checks use portal_permissions template filter.

## 8) Backend business portal design

- Dashboard with KPI cards, top products, low stock, order feed.
- Module navigation by permission.
- Inquiry queue enhancements:
  - list + filter
  - detail panels
  - mark reviewed
  - assign owner
  - add internal notes
  - CSV export

## 9) Public storefront design

- Premium, editorial visual system with custom CSS tokens and typography.
- SEO-ready metadata blocks and structured data support on product pages.
- Utility pages are CMS-backed and editable.

## 10) Stripe integration plan

- PaymentIntent creation in checkout flow.
- Signature-verified Stripe webhook for payment status transitions.
- Production recommendations:
  - idempotent side effects
  - persisted webhook audit records
  - async fulfillment triggers

## 11) Seed data for products and content

- Product category seed command:
  - manage.py seed_catalog_categories
- Utility pages seeded by migration:
  - shipping, refunds, privacy, terms, faq, wholesale, ambassador-program

## 12) Sample dashboard metrics

- Revenue today/week/month
- Orders today/week/month
- AOV
- Top products
- Low stock alerts
- Pending shipments
- Fundraising progress
- Customer growth (30d)

## 13) Local development instructions

- Create venv and install dependencies.
- For local quick checks, run with SQLite env override.
- Run migrate, createsuperuser, runserver.

## 14) Production deployment guidance

- Docker + gunicorn baseline available.
- Use PostgreSQL in production.
- Add reverse proxy, HTTPS, centralized logging/metrics, backups, and worker tier.

## 15) Scalable, clean, modular code posture

Delivered improvements:

- Service-layer package introduced by domain.
- Typed DTO-style serializers for inquiry filters/actions and product CSV rows.
- Product import now service-driven with structured result object.
- Background worker utility introduced for outbound async notifications.
- Portal inquiry workflow converted to form-backed actions.

---

## Implementation roadmap by sprint

### Sprint 1 (completed in this pass)

- Add portal inquiry queues (list/filter).
- Add inquiry detail panel/action flow:
  - mark reviewed
  - assign owner
  - internal notes
  - CSV export
- Add product CSV import in portal.
- Introduce service-layer modules:
  - services/content
  - services/products
  - services/background
- Introduce typed DTO serializers for critical workflows.
- Add foundational automated tests for permissions, checkout, and inquiry transitions.

### Sprint 2

- Convert remaining manual portal POST handlers to form classes (orders/support/returns/coupons/settings).
- Add order/return workflow services and DTO serializers.
- Expand tests for role-specific permission matrices and denied-action assertions.
- Add robust CSV import validation report with downloadable error file.

### Sprint 3

- Move long-running jobs to a dedicated worker stack (Celery + Redis).
- Add async tasks for webhook processing, bulk imports, notification fanout, and report exports.
- Introduce retry/backoff and dead-letter handling for outbound integrations.
- Add observability dashboards and SLO alerts for worker queues.

### Sprint 4

- Add API boundary layer for portal workflows (internal endpoints/serializers).
- Add event-driven audit trail hooks for high-value transitions.
- Introduce domain-level package contracts and stricter static typing checks.
- Add load/perf tests for checkout and high-volume portal operations.
