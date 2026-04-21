from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import (
    PERM_ACTIVITY_VIEW,
    PERM_CONTENT_MANAGE,
    PERM_CONTENT_VIEW,
    PERM_CRM_MANAGE,
    PERM_CRM_VIEW,
    PERM_DASHBOARD_VIEW,
    PERM_FINANCE_MANAGE,
    PERM_FINANCE_VIEW,
    PERM_FULFILLMENT_MANAGE,
    PERM_FUNDRAISING_MANAGE,
    PERM_FUNDRAISING_VIEW,
    PERM_INVENTORY_MANAGE,
    PERM_INVENTORY_VIEW,
    PERM_MARKETING_MANAGE,
    PERM_MARKETING_VIEW,
    PERM_NOTES_MANAGE,
    PERM_NOTES_VIEW,
    PERM_ORDERS_MANAGE,
    PERM_ORDERS_VIEW,
    PERM_PRODUCTS_MANAGE,
    PERM_PRODUCTS_VIEW,
    PERM_PURCHASING_MANAGE,
    PERM_PURCHASING_VIEW,
    PERM_REPORTS_VIEW,
    PERM_RETURNS_MANAGE,
    PERM_RETURNS_VIEW,
    PERM_REVIEWS_MODERATE,
    PERM_REVIEWS_VIEW,
    PERM_SETTINGS_MANAGE,
    PERM_SHIPPING_MANAGE,
    PERM_SHIPPING_VIEW,
    PERM_STAFF_MANAGE,
    PERM_SUPPORT_MANAGE,
    PERM_SUPPORT_VIEW,
)


PORTAL_VIEW_PERMISSIONS = {
    "dashboard": PERM_DASHBOARD_VIEW,
    "product_list": PERM_PRODUCTS_VIEW,
    "product_new": PERM_PRODUCTS_MANAGE,
    "product_import_csv": PERM_PRODUCTS_MANAGE,
    "product_edit": PERM_PRODUCTS_MANAGE,
    "product_variants": PERM_PRODUCTS_MANAGE,
    "product_variant_new": PERM_PRODUCTS_MANAGE,
    "product_variant_edit": PERM_PRODUCTS_MANAGE,
    "product_variant_delete": PERM_PRODUCTS_MANAGE,
    "order_list": PERM_ORDERS_VIEW,
    "order_detail": PERM_ORDERS_MANAGE,
    "order_packing_slip": PERM_ORDERS_VIEW,
    "fulfillment_queue": PERM_FULFILLMENT_MANAGE,
    "inventory_list": PERM_INVENTORY_VIEW,
    "stock_adjustment": PERM_INVENTORY_MANAGE,
    "return_list": PERM_RETURNS_VIEW,
    "return_detail": PERM_RETURNS_MANAGE,
    "return_create": PERM_RETURNS_MANAGE,
    "supplier_list": PERM_PURCHASING_VIEW,
    "supplier_new": PERM_PURCHASING_MANAGE,
    "supplier_edit": PERM_PURCHASING_MANAGE,
    "purchase_order_list": PERM_PURCHASING_VIEW,
    "purchase_order_new": PERM_PURCHASING_MANAGE,
    "purchase_order_edit": PERM_PURCHASING_MANAGE,
    "shipment_list": PERM_SHIPPING_VIEW,
    "shipment_create": PERM_SHIPPING_MANAGE,
    "customer_list": PERM_CRM_VIEW,
    "customer_detail": PERM_CRM_MANAGE,
    "support_ticket_list": PERM_SUPPORT_VIEW,
    "support_ticket_detail": PERM_SUPPORT_MANAGE,
    "review_list": PERM_REVIEWS_VIEW,
    "review_moderate": PERM_REVIEWS_MODERATE,
    "campaign_list": PERM_MARKETING_VIEW,
    "marketing_hub": PERM_MARKETING_VIEW,
    "campaign_new": PERM_MARKETING_MANAGE,
    "campaign_edit": PERM_MARKETING_MANAGE,
    "coupon_list": PERM_MARKETING_VIEW,
    "coupon_new": PERM_MARKETING_MANAGE,
    "coupon_edit": PERM_MARKETING_MANAGE,
    "subscriber_list": PERM_MARKETING_VIEW,
    "content_pages": PERM_CONTENT_VIEW,
    "content_hub": PERM_CONTENT_VIEW,
    "content_page_new": PERM_CONTENT_MANAGE,
    "content_page_edit": PERM_CONTENT_MANAGE,
    "content_blog": PERM_CONTENT_VIEW,
    "content_blog_new": PERM_CONTENT_MANAGE,
    "content_blog_edit": PERM_CONTENT_MANAGE,
    "content_blog_status": PERM_CONTENT_MANAGE,
    "content_guides": PERM_CONTENT_VIEW,
    "content_guide_new": PERM_CONTENT_MANAGE,
    "content_guide_edit": PERM_CONTENT_MANAGE,
    "content_tasting_notes": PERM_CONTENT_VIEW,
    "content_tasting_note_new": PERM_CONTENT_MANAGE,
    "content_tasting_note_edit": PERM_CONTENT_MANAGE,
    "content_journal_posts": PERM_CONTENT_VIEW,
    "content_wholesale_inquiries": PERM_CONTENT_VIEW,
    "content_wholesale_inquiry_detail": PERM_CONTENT_VIEW,
    "content_ambassador_inquiries": PERM_CONTENT_VIEW,
    "content_ambassador_inquiry_detail": PERM_CONTENT_VIEW,
    "fundraising_manage": PERM_FUNDRAISING_VIEW,
    "fundraising_new": PERM_FUNDRAISING_MANAGE,
    "fundraising_edit": PERM_FUNDRAISING_MANAGE,
    "fundraising_donations": PERM_FUNDRAISING_VIEW,
    "finance_overview": PERM_FINANCE_VIEW,
    "expense_add": PERM_FINANCE_MANAGE,
    "reports_overview": PERM_REPORTS_VIEW,
    "notes_list": PERM_NOTES_VIEW,
    "notes_add": PERM_NOTES_MANAGE,
    "activity_log": PERM_ACTIVITY_VIEW,
    "staff_list": PERM_STAFF_MANAGE,
    "business_settings": PERM_SETTINGS_MANAGE,
}


def portal_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_portal_user:
            return redirect("storefront:home")
        url_name = getattr(getattr(request, "resolver_match", None), "url_name", "")
        required_permission = PORTAL_VIEW_PERMISSIONS.get(url_name)
        if required_permission and not request.user.has_portal_permission(required_permission):
            raise PermissionDenied("You do not have permission to access this module.")
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_manager_or_admin:
            raise PermissionDenied("You do not have access to this area.")
        return view_func(request, *args, **kwargs)
    return wrapper


def permission_required(permission_key):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not request.user.is_portal_user:
                return redirect("storefront:home")
            if not request.user.has_portal_permission(permission_key):
                raise PermissionDenied("You do not have permission to perform this action.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
