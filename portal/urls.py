from django.urls import path
from . import views

app_name = "portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Products
    path("products/", views.product_list, name="product_list"),
    path("products/new/", views.product_edit, name="product_new"),
    path("products/import-csv/", views.product_import_csv, name="product_import_csv"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:product_pk>/variants/", views.product_variants, name="product_variants"),
    path("products/<int:product_pk>/variants/new/", views.product_variant_edit, name="product_variant_new"),
    path("products/<int:product_pk>/variants/<int:pk>/edit/", views.product_variant_edit, name="product_variant_edit"),
    path("products/<int:product_pk>/variants/<int:pk>/delete/", views.product_variant_delete, name="product_variant_delete"),
    # Orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/packing-slip/", views.order_packing_slip, name="order_packing_slip"),
    # Fulfillment
    path("fulfillment/", views.fulfillment_queue, name="fulfillment_queue"),
    # Inventory
    path("inventory/", views.inventory_list, name="inventory_list"),
    path("inventory/<int:pk>/adjust/", views.stock_adjustment, name="stock_adjustment"),
    # Returns
    path("returns/", views.return_list, name="return_list"),
    path("returns/<int:pk>/", views.return_detail, name="return_detail"),
    path("returns/create/<int:order_pk>/", views.return_create, name="return_create"),
    # Purchasing & Suppliers
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/new/", views.supplier_edit, name="supplier_new"),
    path("suppliers/<int:pk>/edit/", views.supplier_edit, name="supplier_edit"),
    path("purchase-orders/", views.purchase_order_list, name="purchase_order_list"),
    path("purchase-orders/new/", views.purchase_order_edit, name="purchase_order_new"),
    path("purchase-orders/<int:pk>/edit/", views.purchase_order_edit, name="purchase_order_edit"),
    # Shipping
    path("shipments/", views.shipment_list, name="shipment_list"),
    path("shipments/create/<int:order_pk>/", views.shipment_create, name="shipment_create"),
    # CRM
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    # Support
    path("support/", views.support_ticket_list, name="support_ticket_list"),
    path("support/<int:pk>/", views.support_ticket_detail, name="support_ticket_detail"),
    # Reviews
    path("reviews/", views.review_list, name="review_list"),
    path("reviews/<int:pk>/", views.review_moderate, name="review_moderate"),
    # Marketing
    path("marketing/campaigns/", views.campaign_list, name="campaign_list"),
    path("marketing/hub/", views.marketing_hub, name="marketing_hub"),
    path("marketing/campaigns/new/", views.campaign_edit, name="campaign_new"),
    path("marketing/campaigns/<int:pk>/edit/", views.campaign_edit, name="campaign_edit"),
    path("marketing/coupons/", views.coupon_list, name="coupon_list"),
    path("marketing/coupons/new/", views.coupon_edit, name="coupon_new"),
    path("marketing/coupons/<int:pk>/edit/", views.coupon_edit, name="coupon_edit"),
    path("marketing/subscribers/", views.subscriber_list, name="subscriber_list"),
    # Content
    path("content/pages/", views.content_pages, name="content_pages"),
    path("content/hub/", views.content_hub, name="content_hub"),
    path("content/pages/new/", views.content_page_edit, name="content_page_new"),
    path("content/pages/<int:pk>/edit/", views.content_page_edit, name="content_page_edit"),
    # Content Blocks (editable page sections + images)
    path("content/blocks/", views.content_blocks, name="content_blocks"),
    path("content/blocks/new/", views.content_block_edit, name="content_block_new"),
    path("content/blocks/<int:pk>/edit/", views.content_block_edit, name="content_block_edit"),
    path("content/blocks/<int:pk>/delete/", views.content_block_delete, name="content_block_delete"),
    path("content/blog/", views.content_blog, name="content_blog"),
    path("content/blog/new/", views.content_blog_edit, name="content_blog_new"),
    path("content/blog/<int:pk>/edit/", views.content_blog_edit, name="content_blog_edit"),
    path("content/blog/<int:pk>/status/<str:action>/", views.content_blog_status, name="content_blog_status"),
    path("content/guides/", views.content_guides, name="content_guides"),
    path("content/guides/new/", views.content_guide_edit, name="content_guide_new"),
    path("content/guides/<int:pk>/edit/", views.content_guide_edit, name="content_guide_edit"),
    path("content/tasting-notes/", views.content_tasting_notes, name="content_tasting_notes"),
    path("content/tasting-notes/new/", views.content_tasting_note_edit, name="content_tasting_note_new"),
    path("content/tasting-notes/<int:pk>/edit/", views.content_tasting_note_edit, name="content_tasting_note_edit"),
    path("content/journal/", views.content_journal_posts, name="content_journal_posts"),
    path("content/inquiries/wholesale/", views.content_wholesale_inquiries, name="content_wholesale_inquiries"),
    path("content/inquiries/wholesale/<int:pk>/", views.content_wholesale_inquiry_detail, name="content_wholesale_inquiry_detail"),
    path("content/inquiries/ambassadors/", views.content_ambassador_inquiries, name="content_ambassador_inquiries"),
    path("content/inquiries/ambassadors/<int:pk>/", views.content_ambassador_inquiry_detail, name="content_ambassador_inquiry_detail"),
    # Fundraising
    path("fundraising/", views.fundraising_manage, name="fundraising_manage"),
    path("fundraising/new/", views.fundraising_edit, name="fundraising_new"),
    path("fundraising/<int:pk>/edit/", views.fundraising_edit, name="fundraising_edit"),
    path("fundraising/<int:pk>/donations/", views.fundraising_donations, name="fundraising_donations"),
    # Finance
    path("finance/", views.finance_overview, name="finance_overview"),
    path("finance/expense/add/", views.expense_add, name="expense_add"),
    # Reporting
    path("reports/", views.reports_overview, name="reports_overview"),
    # Notes & Activity
    path("notes/", views.notes_list, name="notes_list"),
    path("notes/add/", views.notes_add, name="notes_add"),
    path("activity/", views.activity_log, name="activity_log"),
    # Staff
    path("staff/", views.staff_list, name="staff_list"),
    # Business Settings
    path("settings/", views.business_settings, name="business_settings"),
]
