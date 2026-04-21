from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.utils.dateparse import parse_datetime
from datetime import timedelta
import csv

from accounts.decorators import portal_required, manager_required
from accounts.models import User
from portal.forms import InquiryAssignForm, InquiryFilterForm, InquiryNoteForm, ProductCsvImportForm
from products.models import Product, Category, ProductVariant, BrewingGuide, TastingNote
from orders.models import Order, OrderItem, Return
from inventory.models import StockRecord, StockMovement
from purchasing.models import Supplier, PurchaseOrder, PurchaseOrderItem
from crm.models import CustomerProfile, Interaction
from marketing.models import Campaign, Coupon, EmailSubscriber
from content.models import AmbassadorInquiry, BlogPost, Page, RitualJournalEntry, WholesaleInquiry
from fundraising.models import FundraisingCampaign, Donation
from finance.models import Transaction, Expense
from shipping.models import Shipment
from reporting.models import DailySummary, ActivityLog
from reviews.models import Review
from support.models import Ticket, TicketMessage
from business_config.models import BusinessSettings
from services.content.inquiry_service import (
    add_ambassador_note,
    add_wholesale_note,
    assign_ambassador,
    assign_wholesale,
    export_ambassador_csv,
    export_wholesale_csv,
    filter_ambassador_inquiries,
    filter_wholesale_inquiries,
    mark_ambassador_reviewed,
    mark_wholesale_reviewed,
)
from services.content.serializers import serialize_inquiry_action, serialize_inquiry_filters
from services.products.import_service import import_products_csv

URL_WHOLESALE_INQUIRY_DETAIL = "portal:content_wholesale_inquiry_detail"
URL_AMBASSADOR_INQUIRY_DETAIL = "portal:content_ambassador_inquiry_detail"
URL_CONTENT_PAGES = "portal:content_pages"
URL_CONTENT_BLOG = "portal:content_blog"


# ── Dashboard ──────────────────────────────────────────

@portal_required
def dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    orders_today = Order.objects.filter(created_at__date=today)
    orders_week = Order.objects.filter(created_at__date__gte=week_ago)
    orders_month = Order.objects.filter(created_at__date__gte=month_ago)

    revenue_today = orders_today.aggregate(s=Sum("total"))["s"] or 0
    revenue_week = orders_week.aggregate(s=Sum("total"))["s"] or 0
    revenue_month = orders_month.aggregate(s=Sum("total"))["s"] or 0

    orders_month_count = orders_month.count()
    avg_order_value = revenue_month / orders_month_count if orders_month_count else 0

    top_products = (
        OrderItem.objects.values("product_name")
        .annotate(total_qty=Sum("quantity"), total_rev=Sum("total_price"))
        .order_by("-total_qty")[:5]
    )

    low_stock_records = StockRecord.objects.filter(quantity_on_hand__lte=F("reorder_level")).select_related("product")[:8]
    pending_shipments = Shipment.objects.filter(status__in=["pending", "label_created", "picked_up", "in_transit"]).count()

    fundraising_active = FundraisingCampaign.objects.filter(status="active")
    fundraising_goal = fundraising_active.aggregate(s=Sum("goal_amount"))["s"] or 0
    fundraising_raised = fundraising_active.aggregate(s=Sum("raised_amount"))["s"] or 0
    fundraising_percent = int((fundraising_raised / fundraising_goal) * 100) if fundraising_goal else 0

    customer_growth_month = User.objects.filter(role="customer", date_joined__date__gte=month_ago).count()

    recent_orders = Order.objects.all()[:10]
    stats = {
        "revenue_today": revenue_today,
        "revenue_week": revenue_week,
        "revenue_month": revenue_month,
        "orders_today": orders_today.count(),
        "orders_week": orders_week.count(),
        "orders_month": orders_month_count,
        "avg_order_value": avg_order_value,
        "top_products": top_products,
        "low_stock": low_stock_records,
        "pending_shipments": pending_shipments,
        "fundraising_raised": fundraising_raised,
        "fundraising_goal": fundraising_goal,
        "fundraising_percent": fundraising_percent,
        "customer_growth_month": customer_growth_month,
        "abandoned_cart_placeholder": "Coming soon",
        "content_performance_placeholder": "Coming soon",
    }
    return render(request, "portal/dashboard.html", {
        "recent_orders": recent_orders,
        "stats": stats,
    })


# ── Products ───────────────────────────────────────────

@portal_required
def product_list(request):
    products = Product.objects.select_related("category").annotate(variant_count=Count("variants")).all()
    q = request.GET.get("q", "")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    cat = request.GET.get("category")
    if cat:
        products = products.filter(category_id=cat)
    paginator = Paginator(products, 25)
    page = paginator.get_page(request.GET.get("page"))
    categories = Category.objects.all()
    return render(request, "portal/products/list.html", {
        "page_obj": page,
        "categories": categories,
        "search_query": q,
    })


@portal_required
def product_import_csv(request):
    result = None
    if request.method == "POST":
        form = ProductCsvImportForm(request.POST, request.FILES)
        if form.is_valid():
            result = import_products_csv(form.cleaned_data["csv_file"])
            messages.success(
                request,
                f"Import complete: {result.created} created, {result.updated} updated, {result.failed} failed.",
            )
    else:
        form = ProductCsvImportForm()
    return render(request, "portal/products/import_csv.html", {"form": form, "result": result})


@portal_required
def product_edit(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        if product:
            obj = product
        else:
            obj = Product()
        obj.name = data.get("name", "")
        obj.sku = data.get("sku", "")
        obj.category_id = data.get("category")
        obj.short_description = data.get("short_description", "")
        obj.description = data.get("description", "")
        obj.price = data.get("price", 0)
        obj.compare_price = data.get("compare_price") or None
        obj.cost = data.get("cost") or None
        obj.origin = data.get("origin", "")
        obj.blend_info = data.get("blend_info", "")
        obj.roast_level = data.get("roast_level", "")
        obj.flavor_notes = data.get("flavor_notes", "")
        obj.aroma_profile = data.get("aroma_profile", "")
        obj.body_profile = data.get("body_profile", "")
        obj.acidity_profile = data.get("acidity_profile", "")
        obj.finish_profile = data.get("finish_profile", "")
        obj.steeping_notes = data.get("steeping_notes", "")
        obj.ritual_description = data.get("ritual_description", "")
        obj.available_sizes = data.get("available_sizes", "")
        obj.grind_options = data.get("grind_options", "")
        obj.tags = data.get("tags", "")
        obj.weight = data.get("weight", "")
        obj.is_subscription_available = data.get("is_subscription_available") == "on"
        obj.is_active = data.get("is_active") == "on"
        obj.is_featured = data.get("is_featured") == "on"
        if request.FILES.get("image"):
            obj.image = request.FILES["image"]
        obj.save()
        messages.success(request, "Product saved.")
        return redirect("portal:product_list")
    categories = Category.objects.all()
    return render(request, "portal/products/edit.html", {
        "product": product,
        "categories": categories,
    })


@portal_required
def product_variants(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    variants = product.variants.all()
    return render(request, "portal/products/variants.html", {"product": product, "variants": variants})


@portal_required
def product_variant_edit(request, product_pk, pk=None):
    product = get_object_or_404(Product, pk=product_pk)
    variant = get_object_or_404(ProductVariant, pk=pk, product=product) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = variant or ProductVariant(product=product)
        obj.name = data.get("name", "")
        obj.sku = data.get("sku", "")
        obj.size = data.get("size", "")
        obj.grind = data.get("grind", "")
        obj.price = data.get("price") or None
        obj.compare_price = data.get("compare_price") or None
        obj.sort_order = data.get("sort_order") or 0
        obj.is_active = data.get("is_active") == "on"
        obj.save()
        messages.success(request, "Variant saved.")
        return redirect("portal:product_variants", product_pk=product.pk)
    return render(request, "portal/products/variant_edit.html", {"product": product, "variant": variant})


@portal_required
@require_POST
def product_variant_delete(request, product_pk, pk):
    product = get_object_or_404(Product, pk=product_pk)
    ProductVariant.objects.filter(pk=pk, product=product).delete()
    messages.success(request, "Variant deleted.")
    return redirect("portal:product_variants", product_pk=product.pk)


# ── Orders ─────────────────────────────────────────────

@portal_required
def order_list(request):
    orders = Order.objects.all()
    status = request.GET.get("status")
    if status:
        orders = orders.filter(status=status)
    q = request.GET.get("q", "")
    if q:
        orders = orders.filter(Q(order_number__icontains=q) | Q(email__icontains=q) | Q(last_name__icontains=q))
    paginator = Paginator(orders, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/orders/list.html", {"page_obj": page, "search_query": q, "current_status": status})


@portal_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action", "status")
        if action == "status":
            new_status = request.POST.get("status")
            if new_status:
                order.status = new_status
                order.save(update_fields=["status"])
                messages.success(request, f"Order updated to {new_status}.")
        elif action == "notes":
            order.notes = request.POST.get("notes", "")
            order.gift_note = request.POST.get("gift_note", "")
            order.save(update_fields=["notes", "gift_note"])
            messages.success(request, "Order notes updated.")
        elif action == "cancel":
            order.status = "cancelled"
            order.save(update_fields=["status"])
            messages.success(request, "Order cancelled.")
        elif action == "refund":
            order.status = "refunded"
            order.save(update_fields=["status"])
            messages.success(request, "Order marked refunded.")
        return redirect("portal:order_detail", pk=pk)
    shipments = order.shipments.all()
    return render(request, "portal/orders/detail.html", {"order": order, "shipments": shipments})


@portal_required
def order_packing_slip(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "portal/orders/packing_slip.html", {"order": order})


# ── Inventory ──────────────────────────────────────────

@portal_required
def inventory_list(request):
    stocks = StockRecord.objects.select_related("product").all()
    low_only = request.GET.get("low")
    if low_only:
        stocks = stocks.filter(quantity_on_hand__lte=F("reorder_level"))
    q = request.GET.get("q", "")
    if q:
        stocks = stocks.filter(product__name__icontains=q)
    paginator = Paginator(stocks, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/inventory/list.html", {"page_obj": page, "search_query": q})


@portal_required
def stock_adjustment(request, pk):
    stock = get_object_or_404(StockRecord, pk=pk)
    if request.method == "POST":
        qty = int(request.POST.get("quantity", 0))
        movement_type = request.POST.get("movement_type", "adjustment")
        notes = request.POST.get("notes", "")
        StockMovement.objects.create(
            product=stock.product,
            movement_type=movement_type,
            quantity=qty,
            notes=notes,
            created_by=request.user,
        )
        if movement_type in ("in", "return"):
            stock.quantity_on_hand += abs(qty)
        elif movement_type == "out":
            stock.quantity_on_hand -= abs(qty)
        else:
            stock.quantity_on_hand = qty
        stock.save()
        messages.success(request, "Stock updated.")
        return redirect("portal:inventory_list")
    movements = StockMovement.objects.filter(product=stock.product)[:20]
    return render(request, "portal/inventory/adjustment.html", {"stock": stock, "movements": movements})


# ── Purchasing & Suppliers ─────────────────────────────

@portal_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    q = request.GET.get("q", "")
    if q:
        suppliers = suppliers.filter(name__icontains=q)
    return render(request, "portal/purchasing/suppliers.html", {"suppliers": suppliers, "search_query": q})


@portal_required
def supplier_edit(request, pk=None):
    supplier = get_object_or_404(Supplier, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = supplier or Supplier()
        obj.name = data.get("name", "")
        obj.contact_name = data.get("contact_name", "")
        obj.email = data.get("email", "")
        obj.phone = data.get("phone", "")
        obj.website = data.get("website", "")
        obj.address = data.get("address", "")
        obj.notes = data.get("notes", "")
        obj.is_active = data.get("is_active") == "on"
        obj.save()
        messages.success(request, "Supplier saved.")
        return redirect("portal:supplier_list")
    return render(request, "portal/purchasing/supplier_edit.html", {"supplier": supplier})


@portal_required
def purchase_order_list(request):
    pos = PurchaseOrder.objects.select_related("supplier").all()
    status = request.GET.get("status")
    if status:
        pos = pos.filter(status=status)
    paginator = Paginator(pos, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/purchasing/po_list.html", {"page_obj": page, "current_status": status})


@portal_required
def purchase_order_edit(request, pk=None):
    po = get_object_or_404(PurchaseOrder, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = po or PurchaseOrder()
        obj.po_number = data.get("po_number", "")
        obj.supplier_id = data.get("supplier")
        obj.status = data.get("status", "draft")
        obj.notes = data.get("notes", "")
        obj.expected_date = data.get("expected_date") or None
        obj.created_by = request.user
        obj.save()
        messages.success(request, "Purchase order saved.")
        return redirect("portal:purchase_order_list")
    suppliers = Supplier.objects.filter(is_active=True)
    return render(request, "portal/purchasing/po_edit.html", {"po": po, "suppliers": suppliers})


# ── CRM ────────────────────────────────────────────────

@portal_required
def customer_list(request):
    customers = User.objects.filter(role="customer")
    q = request.GET.get("q", "")
    if q:
        customers = customers.filter(Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    paginator = Paginator(customers, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/crm/customer_list.html", {"page_obj": page, "search_query": q})


@portal_required
def customer_detail(request, pk):
    customer = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=customer)[:10]
    interactions = Interaction.objects.filter(customer=customer)[:10]
    profile, _ = CustomerProfile.objects.get_or_create(user=customer)
    if request.method == "POST" and request.POST.get("action") == "add_note":
        Interaction.objects.create(
            customer=customer,
            interaction_type="note",
            subject=request.POST.get("subject", ""),
            body=request.POST.get("body", ""),
            created_by=request.user,
        )
        messages.success(request, "Note added.")
        return redirect("portal:customer_detail", pk=pk)
    return render(request, "portal/crm/customer_detail.html", {
        "customer": customer,
        "orders": orders,
        "interactions": interactions,
        "profile": profile,
    })


# ── Shipping & Fulfillment ─────────────────────────────

@portal_required
def shipment_list(request):
    shipments = Shipment.objects.select_related("order").all()
    status = request.GET.get("status")
    if status:
        shipments = shipments.filter(status=status)
    paginator = Paginator(shipments, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/shipping/list.html", {"page_obj": page, "current_status": status})


@portal_required
def shipment_create(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if request.method == "POST":
        Shipment.objects.create(
            order=order,
            carrier=request.POST.get("carrier", "usps"),
            tracking_number=request.POST.get("tracking_number", ""),
            status=request.POST.get("status", "pending"),
            notes=request.POST.get("notes", ""),
            created_by=request.user,
        )
        order.status = "shipped"
        order.save(update_fields=["status"])
        messages.success(request, "Shipment created.")
        return redirect("portal:order_detail", pk=order_pk)
    return render(request, "portal/shipping/create.html", {"order": order})


# ── Finance ────────────────────────────────────────────

@portal_required
def finance_overview(request):
    today = timezone.now().date()
    thirty_days = today - timedelta(days=30)
    transactions = Transaction.objects.filter(date__gte=thirty_days)
    total_income = transactions.filter(transaction_type="sale").aggregate(s=Sum("amount"))["s"] or 0
    total_expenses_val = Expense.objects.filter(date__gte=thirty_days).aggregate(s=Sum("amount"))["s"] or 0
    recent_transactions = Transaction.objects.all()[:20]
    recent_expenses = Expense.objects.all()[:20]
    return render(request, "portal/finance/overview.html", {
        "total_income": total_income,
        "total_expenses": total_expenses_val,
        "net_profit": total_income - total_expenses_val,
        "recent_transactions": recent_transactions,
        "recent_expenses": recent_expenses,
    })


@portal_required
def expense_add(request):
    if request.method == "POST":
        Expense.objects.create(
            description=request.POST.get("description", ""),
            amount=request.POST.get("amount", 0),
            category=request.POST.get("category", "other"),
            vendor=request.POST.get("vendor", ""),
            date=request.POST.get("date", timezone.now().date()),
            notes=request.POST.get("notes", ""),
            created_by=request.user,
        )
        messages.success(request, "Expense recorded.")
        return redirect("portal:finance_overview")
    return render(request, "portal/finance/expense_add.html")


# ── Marketing ──────────────────────────────────────────

@portal_required
def campaign_list(request):
    campaigns = Campaign.objects.all()
    return render(request, "portal/marketing/campaigns.html", {"campaigns": campaigns})


@portal_required
def marketing_hub(request):
    stats = {
        "newsletter_signups": EmailSubscriber.objects.count(),
        "active_promos": Coupon.objects.filter(is_active=True).count(),
        "active_campaigns": Campaign.objects.filter(status="active").count(),
    }
    modules = [
        {"label": "Homepage banners", "url_name": URL_CONTENT_PAGES},
        {"label": "Featured collections", "url_name": "portal:product_list"},
        {"label": "Ambassadors", "url_name": "portal:content_ambassador_inquiries"},
        {"label": "Wholesale leads", "url_name": "portal:content_wholesale_inquiries"},
        {"label": "Referral sources", "url_name": "portal:customer_list"},
        {"label": "Landing pages", "url_name": URL_CONTENT_PAGES},
        {"label": "Social content planning", "url_name": URL_CONTENT_BLOG},
    ]
    return render(request, "portal/marketing/hub.html", {"stats": stats, "modules": modules})


@portal_required
def campaign_edit(request, pk=None):
    campaign = get_object_or_404(Campaign, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = campaign or Campaign()
        obj.name = data.get("name", "")
        obj.channel = data.get("channel", "email")
        obj.status = data.get("status", "draft")
        obj.description = data.get("description", "")
        obj.budget = data.get("budget") or None
        obj.target_audience = data.get("target_audience", "")
        obj.start_date = data.get("start_date") or None
        obj.end_date = data.get("end_date") or None
        obj.save()
        messages.success(request, "Campaign saved.")
        return redirect("portal:campaign_list")
    return render(request, "portal/marketing/campaign_edit.html", {"campaign": campaign})


@portal_required
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, "portal/marketing/coupons.html", {"coupons": coupons})


@portal_required
def subscriber_list(request):
    subs = EmailSubscriber.objects.all()
    paginator = Paginator(subs, 50)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/marketing/subscribers.html", {"page_obj": page})


# ── Content Management ─────────────────────────────────

@portal_required
def content_pages(request):
    pages = Page.objects.all()
    blog_posts = BlogPost.objects.all()
    return render(request, "portal/content/pages.html", {"pages": pages, "blog_posts": blog_posts})


@portal_required
def content_hub(request):
    stats = {
        "pages": Page.objects.count(),
        "guides": BrewingGuide.objects.count(),
        "tasting_notes": TastingNote.objects.count(),
        "journal_posts": BlogPost.objects.count(),
        "wholesale_inquiries": WholesaleInquiry.objects.count(),
        "ambassador_inquiries": AmbassadorInquiry.objects.count(),
    }
    placeholders = ["Homepage sections", "About page content", "Contact page content", "FAQs", "Policy pages", "Media library"]
    return render(request, "portal/content/hub.html", {"stats": stats, "placeholders": placeholders})


@portal_required
def content_guides(request):
    guides = BrewingGuide.objects.select_related("product").all()
    q = request.GET.get("q", "")
    if q:
        guides = guides.filter(Q(title__icontains=q) | Q(method__icontains=q) | Q(tags__icontains=q))
    return render(request, "portal/content/guides.html", {"guides": guides, "search_query": q})


@portal_required
def content_guide_edit(request, pk=None):
    guide = get_object_or_404(BrewingGuide, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = guide or BrewingGuide()
        obj.title = data.get("title", "")
        obj.product_id = data.get("product") or None
        obj.guide_type = data.get("guide_type", "other")
        obj.audience_level = data.get("audience_level", "beginner")
        obj.tags = data.get("tags", "")
        obj.is_premium_featured = data.get("is_premium_featured") == "on"
        obj.method = data.get("method", "")
        obj.description = data.get("description", "")
        obj.instructions = data.get("instructions", "")
        obj.water_temp = data.get("water_temp", "")
        obj.brew_time = data.get("brew_time", "")
        obj.grind_size = data.get("grind_size", "")
        obj.ratio = data.get("ratio", "")
        obj.is_published = data.get("is_published") == "on"
        if request.FILES.get("image"):
            obj.image = request.FILES["image"]
        obj.save()
        messages.success(request, "Guide saved.")
        return redirect("portal:content_guides")
    products = Product.objects.filter(is_active=True)
    return render(request, "portal/content/guide_edit.html", {"guide": guide, "products": products})


@portal_required
def content_tasting_notes(request):
    notes = TastingNote.objects.select_related("product").all()
    q = request.GET.get("q", "")
    if q:
        notes = notes.filter(Q(title__icontains=q) | Q(tags__icontains=q) | Q(product__name__icontains=q))
    return render(request, "portal/content/tasting_notes.html", {"notes": notes, "search_query": q})


@portal_required
def content_tasting_note_edit(request, pk=None):
    note = get_object_or_404(TastingNote, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = note or TastingNote()
        obj.product_id = data.get("product")
        obj.title = data.get("title", "")
        obj.body = data.get("body", "")
        obj.aroma = data.get("aroma", "")
        obj.flavor = data.get("flavor", "")
        obj.finish = data.get("finish", "")
        obj.origin = data.get("origin", "")
        obj.pairings = data.get("pairings", "")
        obj.style_notes = data.get("style_notes", "")
        obj.tags = data.get("tags", "")
        obj.rating = data.get("rating") or 5
        obj.save()
        messages.success(request, "Tasting note saved.")
        return redirect("portal:content_tasting_notes")
    products = Product.objects.filter(is_active=True)
    return render(request, "portal/content/tasting_note_edit.html", {"note": note, "products": products})


@portal_required
def content_journal_posts(request):
    posts = BlogPost.objects.filter(entry_type__in=[
        "slow_living", "ritual_routines", "seasonal_reflections", "brewing_philosophy", "brand_storytelling"
    ])
    q = request.GET.get("q", "")
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(tags__icontains=q))
    return render(request, "portal/content/journal_posts.html", {"posts": posts, "search_query": q})


@portal_required
def content_wholesale_inquiries(request):
    form = InquiryFilterForm(request.GET or None)
    if form.is_valid():
        filter_dto = serialize_inquiry_filters(form.cleaned_data)
    else:
        filter_dto = serialize_inquiry_filters({})

    inquiries = filter_wholesale_inquiries(filter_dto)
    if request.GET.get("export") == "csv":
        return export_wholesale_csv(inquiries)

    paginator = Paginator(inquiries, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/content/wholesale_inquiries.html", {
        "page_obj": page,
        "search_query": filter_dto.q,
        "from_date": filter_dto.from_date,
        "to_date": filter_dto.to_date,
    })


@portal_required
def content_ambassador_inquiries(request):
    form = InquiryFilterForm(request.GET or None)
    if form.is_valid():
        filter_dto = serialize_inquiry_filters(form.cleaned_data)
    else:
        filter_dto = serialize_inquiry_filters({})

    inquiries = filter_ambassador_inquiries(filter_dto)
    if request.GET.get("export") == "csv":
        return export_ambassador_csv(inquiries)

    paginator = Paginator(inquiries, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/content/ambassador_inquiries.html", {
        "page_obj": page,
        "search_query": filter_dto.q,
        "platform_query": filter_dto.platform,
        "from_date": filter_dto.from_date,
        "to_date": filter_dto.to_date,
    })


@portal_required
def content_wholesale_inquiry_detail(request, pk):
    inquiry = get_object_or_404(WholesaleInquiry.objects.select_related("assigned_to", "reviewed_by"), pk=pk)
    assign_form = InquiryAssignForm(prefix="assign", initial={"assigned_to": inquiry.assigned_to})
    note_form = InquiryNoteForm(prefix="note")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "mark_reviewed":
            mark_wholesale_reviewed(inquiry, request.user)
            messages.success(request, "Inquiry marked as reviewed.")
            return redirect(URL_WHOLESALE_INQUIRY_DETAIL, pk=pk)
        if action == "assign":
            assign_form = InquiryAssignForm(request.POST, prefix="assign")
            if assign_form.is_valid():
                action_dto = serialize_inquiry_action(assign_form.cleaned_data)
                assign_wholesale(inquiry, action_dto.assigned_to_id)
                messages.success(request, "Owner assignment updated.")
                return redirect(URL_WHOLESALE_INQUIRY_DETAIL, pk=pk)
        if action == "add_note":
            note_form = InquiryNoteForm(request.POST, prefix="note")
            if note_form.is_valid():
                action_dto = serialize_inquiry_action(note_form.cleaned_data)
                add_wholesale_note(inquiry, request.user, action_dto.note)
                messages.success(request, "Internal note added.")
                return redirect(URL_WHOLESALE_INQUIRY_DETAIL, pk=pk)

    notes = inquiry.internal_notes.select_related("author").all()
    return render(request, "portal/content/wholesale_inquiry_detail.html", {
        "inquiry": inquiry,
        "assign_form": assign_form,
        "note_form": note_form,
        "notes": notes,
    })


@portal_required
def content_ambassador_inquiry_detail(request, pk):
    inquiry = get_object_or_404(AmbassadorInquiry.objects.select_related("assigned_to", "reviewed_by"), pk=pk)
    assign_form = InquiryAssignForm(prefix="assign", initial={"assigned_to": inquiry.assigned_to})
    note_form = InquiryNoteForm(prefix="note")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "mark_reviewed":
            mark_ambassador_reviewed(inquiry, request.user)
            messages.success(request, "Inquiry marked as reviewed.")
            return redirect(URL_AMBASSADOR_INQUIRY_DETAIL, pk=pk)
        if action == "assign":
            assign_form = InquiryAssignForm(request.POST, prefix="assign")
            if assign_form.is_valid():
                action_dto = serialize_inquiry_action(assign_form.cleaned_data)
                assign_ambassador(inquiry, action_dto.assigned_to_id)
                messages.success(request, "Owner assignment updated.")
                return redirect(URL_AMBASSADOR_INQUIRY_DETAIL, pk=pk)
        if action == "add_note":
            note_form = InquiryNoteForm(request.POST, prefix="note")
            if note_form.is_valid():
                action_dto = serialize_inquiry_action(note_form.cleaned_data)
                add_ambassador_note(inquiry, request.user, action_dto.note)
                messages.success(request, "Internal note added.")
                return redirect(URL_AMBASSADOR_INQUIRY_DETAIL, pk=pk)

    notes = inquiry.internal_notes.select_related("author").all()
    return render(request, "portal/content/ambassador_inquiry_detail.html", {
        "inquiry": inquiry,
        "assign_form": assign_form,
        "note_form": note_form,
        "notes": notes,
    })


@portal_required
def content_page_edit(request, pk=None):
    page = get_object_or_404(Page, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = page or Page()
        obj.title = data.get("title", "")
        obj.body = data.get("body", "")
        obj.meta_title = data.get("meta_title", "")
        obj.meta_description = data.get("meta_description", "")
        obj.is_published = data.get("is_published") == "on"
        obj.save()
        messages.success(request, "Page saved.")
        return redirect(URL_CONTENT_PAGES)
    return render(request, "portal/content/page_edit.html", {"page": page})


@portal_required
def content_blog(request):
    posts = BlogPost.objects.select_related("author").all()
    status = request.GET.get("status", "")
    q = request.GET.get("q", "")
    if status:
        posts = posts.filter(status=status)
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(tags__icontains=q))
    return render(request, "portal/content/blog.html", {
        "posts": posts,
        "current_status": status,
        "search_query": q,
        "status_choices": BlogPost.STATUS_CHOICES,
    })


# ── Fundraising Management ─────────────────────────────

@portal_required
def fundraising_manage(request):
    campaigns = FundraisingCampaign.objects.all()
    stats = {
        "active": campaigns.filter(status="active").count(),
        "draft": campaigns.filter(status="draft").count(),
        "total_goal": campaigns.aggregate(s=Sum("goal_amount"))["s"] or 0,
        "total_raised": campaigns.aggregate(s=Sum("raised_amount"))["s"] or 0,
    }
    placeholders = ["Review applications", "Assign payout percentages", "Campaign sales attribution", "Organization earnings export", "Fundraiser bundles"]
    return render(request, "portal/fundraising/list.html", {"campaigns": campaigns, "stats": stats, "placeholders": placeholders})


@portal_required
def fundraising_edit(request, pk=None):
    campaign = get_object_or_404(FundraisingCampaign, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = campaign or FundraisingCampaign()
        obj.title = data.get("title", "")
        obj.description = data.get("description", "")
        obj.story = data.get("story", "")
        obj.goal_amount = data.get("goal_amount", 0)
        obj.beneficiary = data.get("beneficiary", "")
        obj.status = data.get("status", "draft")
        obj.start_date = data.get("start_date") or None
        obj.end_date = data.get("end_date") or None
        if request.FILES.get("image"):
            obj.image = request.FILES["image"]
        obj.save()
        messages.success(request, "Campaign saved.")
        return redirect("portal:fundraising_manage")
    return render(request, "portal/fundraising/edit.html", {"campaign": campaign})


@portal_required
def fundraising_donations(request, pk):
    campaign = get_object_or_404(FundraisingCampaign, pk=pk)
    donations = campaign.donations.all()
    return render(request, "portal/fundraising/donations.html", {"campaign": campaign, "donations": donations})


# ── Reporting ──────────────────────────────────────────

@portal_required
def reports_overview(request):
    today = timezone.now().date()
    thirty_days = today - timedelta(days=30)
    stats = {
        "orders_30d": Order.objects.filter(created_at__date__gte=thirty_days).count(),
        "revenue_30d": Order.objects.filter(created_at__date__gte=thirty_days).aggregate(s=Sum("total"))["s"] or 0,
        "new_customers_30d": User.objects.filter(date_joined__date__gte=thirty_days, role="customer").count(),
        "top_products": OrderItem.objects.values("product_name").annotate(
            total_qty=Sum("quantity"), total_rev=Sum("total_price")
        ).order_by("-total_qty")[:10],
        "orders_by_status": Order.objects.values("status").annotate(count=Count("id")),
    }

    export = request.GET.get("export")
    if export:
        return _export_report_csv(export)

    return render(request, "portal/reporting/overview.html", {"stats": stats})


# ── Staff Management ───────────────────────────────────

@manager_required
def staff_list(request):
    staff = User.objects.exclude(role="customer")
    return render(request, "portal/staff/list.html", {"staff_members": staff})


# ── Fulfillment Queue ──────────────────────────────────

@portal_required
def fulfillment_queue(request):
    orders = Order.objects.filter(status__in=["confirmed", "processing"]).select_related()
    q = request.GET.get("q", "")
    if q:
        orders = orders.filter(Q(order_number__icontains=q) | Q(email__icontains=q))
    paginator = Paginator(orders, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/fulfillment/queue.html", {"page_obj": page, "search_query": q})


# ── Returns ────────────────────────────────────────────

@portal_required
def return_list(request):
    returns = Return.objects.select_related("order", "item", "processed_by").all()
    status = request.GET.get("status")
    if status:
        returns = returns.filter(status=status)
    q = request.GET.get("q", "")
    if q:
        returns = returns.filter(
            Q(return_number__icontains=q) | Q(order__order_number__icontains=q)
        )
    paginator = Paginator(returns, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/returns/list.html", {
        "page_obj": page,
        "search_query": q,
        "current_status": status,
    })


@portal_required
def return_detail(request, pk):
    ret = get_object_or_404(Return, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_status":
            ret.status = request.POST.get("status", ret.status)
            ret.resolution_notes = request.POST.get("resolution_notes", ret.resolution_notes)
            ret.refund_amount = request.POST.get("refund_amount", ret.refund_amount) or 0
            ret.processed_by = request.user
            ret.save()
            messages.success(request, f"Return {ret.return_number} updated.")
            return redirect("portal:return_detail", pk=pk)
    return render(request, "portal/returns/detail.html", {"ret": ret})


@portal_required
def return_create(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if request.method == "POST":
        ret = Return.objects.create(
            order=order,
            item_id=request.POST.get("item") or None,
            reason=request.POST.get("reason", "other"),
            description=request.POST.get("description", ""),
            processed_by=request.user,
        )
        messages.success(request, f"Return {ret.return_number} created.")
        return redirect("portal:return_detail", pk=ret.pk)
    return render(request, "portal/returns/create.html", {"order": order})


# ── Reviews Moderation ─────────────────────────────────

@portal_required
def review_list(request):
    reviews = Review.objects.select_related("product", "user").all()
    status = request.GET.get("status")
    if status:
        reviews = reviews.filter(status=status)
    paginator = Paginator(reviews, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/reviews/list.html", {
        "page_obj": page,
        "current_status": status,
    })


@portal_required
def review_moderate(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            review.status = "approved"
            review.save(update_fields=["status"])
            messages.success(request, "Review approved.")
        elif action == "reject":
            review.status = "rejected"
            review.save(update_fields=["status"])
            messages.success(request, "Review rejected.")
        return redirect("portal:review_list")
    return render(request, "portal/reviews/detail.html", {"review": review})


# ── Support Tickets ────────────────────────────────────

@portal_required
def support_ticket_list(request):
    tickets = Ticket.objects.select_related("user", "assigned_to").all()
    status = request.GET.get("status")
    if status:
        tickets = tickets.filter(status=status)
    q = request.GET.get("q", "")
    if q:
        tickets = tickets.filter(
            Q(ticket_number__icontains=q) | Q(subject__icontains=q) | Q(email__icontains=q)
        )
    paginator = Paginator(tickets, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/support/list.html", {
        "page_obj": page,
        "search_query": q,
        "current_status": status,
    })


@portal_required
def support_ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket_messages = ticket.messages.select_related("author").all()
    staff_members = User.objects.exclude(role="customer")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "reply":
            body = request.POST.get("body", "").strip()
            if body:
                TicketMessage.objects.create(
                    ticket=ticket,
                    author=request.user,
                    body=body,
                    is_staff_reply=True,
                )
                if ticket.status == "open":
                    ticket.status = "in_progress"
                    ticket.save(update_fields=["status"])
                messages.success(request, "Reply sent.")
        elif action == "update":
            ticket.status = request.POST.get("status", ticket.status)
            ticket.priority = request.POST.get("priority", ticket.priority)
            assigned = request.POST.get("assigned_to")
            ticket.assigned_to_id = assigned if assigned else None
            ticket.save()
            messages.success(request, "Ticket updated.")
        return redirect("portal:support_ticket_detail", pk=pk)
    return render(request, "portal/support/detail.html", {
        "ticket": ticket,
        "ticket_messages": ticket_messages,
        "staff_members": staff_members,
    })


# ── Blog CRUD ──────────────────────────────────────────

@portal_required
def content_blog_edit(request, pk=None):
    post = get_object_or_404(BlogPost, pk=pk) if pk else None
    if request.method == "POST":
        obj = _apply_blog_form_data(post or BlogPost(), request)
        obj.save()
        messages.success(request, "Blog post saved.")
        return redirect(URL_CONTENT_BLOG)
    return render(request, "portal/content/blog_edit.html", {
        "post": post,
        "entry_type_choices": BlogPost.ENTRY_TYPE_CHOICES,
        "status_choices": BlogPost.STATUS_CHOICES,
    })


@portal_required
@require_POST
def content_blog_status(request, pk, action):
    post = get_object_or_404(BlogPost, pk=pk)
    if action == "publish":
        post.status = "published"
        post.published_at = timezone.now()
        post.save(update_fields=["status", "published_at", "is_published", "updated_at"])
        messages.success(request, "Post published.")
    elif action == "unpublish":
        post.status = "unpublished"
        post.save(update_fields=["status", "is_published", "updated_at"])
        messages.success(request, "Post unpublished.")
    return redirect(URL_CONTENT_BLOG)


def _apply_blog_form_data(obj, request):
    data = request.POST
    obj.title = data.get("title", "")
    obj.entry_type = data.get("entry_type", "slow_living")
    obj.tags = data.get("tags", "")
    obj.excerpt = data.get("excerpt", "")
    obj.body = data.get("body", "")
    obj.status = data.get("status", "draft")
    obj.author = request.user

    published_at = _parse_portal_datetime(data.get("published_at", ""))
    if published_at is not None:
        obj.published_at = published_at
    elif obj.status in ["draft", "unpublished"]:
        obj.published_at = None

    if obj.status == "published" and not obj.published_at:
        obj.published_at = timezone.now()

    if request.FILES.get("image"):
        obj.image = request.FILES["image"]
    return obj


def _parse_portal_datetime(raw_value):
    value = (raw_value or "").strip()
    if not value:
        return None
    parsed = parse_datetime(value)
    if parsed is None:
        return None
    return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed


def _export_report_csv(report_type):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{report_type}_report.csv"'
    writer = csv.writer(response)

    if report_type == "orders":
        writer.writerow(["Order", "Date", "Status", "Customer", "Total"])
        for order in Order.objects.all().order_by("-created_at")[:500]:
            writer.writerow([order.order_number, order.created_at.date(), order.status, order.email, order.total])
    elif report_type == "inventory":
        writer.writerow(["Product", "On Hand", "Reserved", "Available", "Reorder Level", "Location"])
        for stock in StockRecord.objects.select_related("product").all():
            writer.writerow([stock.product.name, stock.quantity_on_hand, stock.quantity_reserved, stock.available, stock.reorder_level, stock.location])
    elif report_type == "refunds":
        writer.writerow(["Return #", "Order", "Status", "Reason", "Refund Amount", "Created"])
        for ret in Return.objects.select_related("order").all().order_by("-created_at")[:500]:
            writer.writerow([ret.return_number, ret.order.order_number, ret.status, ret.reason, ret.refund_amount, ret.created_at.date()])
    elif report_type == "low_stock":
        writer.writerow(["Product", "Available", "Reorder Level", "Location"])
        for stock in StockRecord.objects.filter(quantity_on_hand__lte=F("reorder_level")).select_related("product"):
            writer.writerow([stock.product.name, stock.available, stock.reorder_level, stock.location])
    else:
        writer.writerow(["Metric", "Value"])
        revenue_30d = Order.objects.filter(created_at__date__gte=timezone.now().date() - timedelta(days=30)).aggregate(s=Sum("total"))["s"] or 0
        writer.writerow(["Revenue (30d)", revenue_30d])
        writer.writerow(["Orders (30d)", Order.objects.filter(created_at__date__gte=timezone.now().date() - timedelta(days=30)).count()])
        writer.writerow(["Expenses (30d)", Expense.objects.filter(date__gte=timezone.now().date() - timedelta(days=30)).aggregate(s=Sum("amount"))["s"] or 0])

    return response


# ── Coupon CRUD ────────────────────────────────────────

@portal_required
def coupon_edit(request, pk=None):
    coupon = get_object_or_404(Coupon, pk=pk) if pk else None
    if request.method == "POST":
        data = request.POST
        obj = coupon or Coupon()
        obj.code = data.get("code", "").upper()
        obj.description = data.get("description", "")
        obj.discount_type = data.get("discount_type", "percent")
        obj.discount_value = data.get("discount_value", 0)
        obj.min_order = data.get("min_order", 0) or 0
        obj.max_uses = data.get("max_uses") or None
        obj.is_active = data.get("is_active") == "on"
        obj.valid_from = data.get("valid_from")
        obj.valid_until = data.get("valid_until")
        obj.save()
        messages.success(request, "Coupon saved.")
        return redirect("portal:coupon_list")
    return render(request, "portal/marketing/coupon_edit.html", {"coupon": coupon})


# ── Business Settings ──────────────────────────────────

@manager_required
def business_settings(request):
    settings_obj = BusinessSettings.load()
    if request.method == "POST":
        data = request.POST
        settings_obj.store_name = data.get("store_name", settings_obj.store_name)
        settings_obj.tagline = data.get("tagline", "")
        settings_obj.email = data.get("email", "")
        settings_obj.phone = data.get("phone", "")
        settings_obj.address_line1 = data.get("address_line1", "")
        settings_obj.address_line2 = data.get("address_line2", "")
        settings_obj.city = data.get("city", "")
        settings_obj.state = data.get("state", "")
        settings_obj.postal_code = data.get("postal_code", "")
        settings_obj.country = data.get("country", "US")
        settings_obj.currency = data.get("currency", "USD")
        settings_obj.tax_rate = data.get("tax_rate", 0) or 0
        settings_obj.free_shipping_threshold = data.get("free_shipping_threshold", 75) or 75
        settings_obj.instagram_url = data.get("instagram_url", "")
        settings_obj.facebook_url = data.get("facebook_url", "")
        settings_obj.twitter_url = data.get("twitter_url", "")
        settings_obj.save()
        messages.success(request, "Business settings saved.")
        return redirect("portal:business_settings")
    return render(request, "portal/settings/edit.html", {"settings_obj": settings_obj})


# ── Activity Log ───────────────────────────────────────

@portal_required
def activity_log(request):
    logs = ActivityLog.objects.select_related("user").all()
    action_filter = request.GET.get("action")
    if action_filter:
        logs = logs.filter(action=action_filter)
    entity_filter = request.GET.get("entity_type")
    if entity_filter:
        logs = logs.filter(entity_type=entity_filter)
    q = request.GET.get("q", "")
    if q:
        logs = logs.filter(
            Q(entity_label__icontains=q) | Q(description__icontains=q)
        )
    paginator = Paginator(logs, 50)
    page = paginator.get_page(request.GET.get("page"))
    entity_types = ActivityLog.objects.values_list("entity_type", flat=True).distinct()
    return render(request, "portal/activity/list.html", {
        "page_obj": page,
        "search_query": q,
        "current_action": action_filter,
        "entity_types": entity_types,
    })


# ── Notes (Internal) ──────────────────────────────────

@portal_required
def notes_list(request):
    notes = Interaction.objects.filter(interaction_type="note").select_related("customer", "created_by")
    q = request.GET.get("q", "")
    if q:
        notes = notes.filter(Q(subject__icontains=q) | Q(body__icontains=q))
    paginator = Paginator(notes, 25)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "portal/notes/list.html", {"page_obj": page, "search_query": q})


@portal_required
def notes_add(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer")
        Interaction.objects.create(
            customer_id=customer_id,
            interaction_type="note",
            subject=request.POST.get("subject", ""),
            body=request.POST.get("body", ""),
            created_by=request.user,
        )
        messages.success(request, "Note added.")
        return redirect("portal:notes_list")
    customers = User.objects.filter(role="customer").order_by("email")
    return render(request, "portal/notes/add.html", {"customers": customers})
