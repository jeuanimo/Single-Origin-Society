from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q
from products.models import Product, Category, BrewingGuide, TastingNote
from orders.models import Order, OrderItem
from fundraising.models import FundraisingCampaign
from content.forms import AmbassadorInquiryForm, WholesaleInquiryForm
from content.models import Page, BlogPost, RitualJournalEntry
from marketing.models import EmailSubscriber, Coupon, CampaignLandingPage, HomepagePromoBlock
from business_config.models import BusinessSettings
from reviews.models import Review
from customers.models import WishlistItem
from services.background.worker import enqueue
from services.content.notifications import send_inquiry_notification
import stripe

URL_CART = "storefront:cart"
URL_HOME = "storefront:home"
TEMPLATE_INFO_PAGE = "storefront/info_page.html"
INFO_BODY_FALLBACK = "<p>Content coming soon.</p>"

stripe.api_key = settings.STRIPE_SECRET_KEY

POLICY_FALLBACKS = {
    "shipping": {
        "title": "Shipping Policy",
        "body": "<p>Orders are typically processed within 1-2 business days.</p><p>Complimentary shipping is available on qualifying orders. Delivery windows vary by destination and carrier.</p>",
    },
    "refunds": {
        "title": "Refund Policy",
        "body": "<p>If something is not right, contact us within 14 days of delivery.</p><p>Eligible items may be refunded or replaced according to condition and product type.</p>",
    },
    "privacy": {
        "title": "Privacy Policy",
        "body": "<p>We collect only the information needed to fulfill orders and improve your experience.</p><p>We do not sell personal data to third parties.</p>",
    },
    "terms": {
        "title": "Terms of Service",
        "body": "<p>By using this site, you agree to these terms and all applicable laws.</p><p>Product availability, pricing, and policies may be updated from time to time.</p>",
    },
}

INFO_PAGE_FALLBACKS = {
    "faq": {
        "title": "Frequently Asked Questions",
        "body": "<h2>Orders</h2><p>Most orders ship within 1-2 business days.</p><h2>Freshness</h2><p>All coffee is roasted in small batches for freshness.</p><h2>Support</h2><p>Need help? Contact us and we will respond promptly.</p>",
    },
    "wholesale": {
        "title": "Wholesale",
        "body": "<p>We partner with cafes, hotels, and retailers seeking exceptional coffee and tea.</p><p>Contact us with your business details and projected volume to begin onboarding.</p>",
    },
    "ambassador-program": {
        "title": "Ambassador Program",
        "body": "<p>Join our ambassador community to share the ritual and earn exclusive benefits.</p><p>Applications are reviewed on a rolling basis.</p>",
    },
}


def home(request):
    featured = Product.objects.filter(is_featured=True, is_active=True)[:6]
    featured_coffee = Product.objects.filter(
        is_active=True,
        category__category_type="coffee",
    ).order_by("-is_featured", "-created_at")[:4]
    featured_tea = Product.objects.filter(
        is_active=True,
        category__category_type="tea",
    ).order_by("-is_featured", "-created_at")[:4]
    gift_sets = Product.objects.filter(
        is_active=True,
        category__category_type="gift_sets",
    ).order_by("-is_featured", "-created_at")[:4]

    categories = Category.objects.filter(is_active=True)
    campaigns = FundraisingCampaign.objects.filter(status="active")[:2]
    fundraising_feature = campaigns.first()
    promo_blocks = HomepagePromoBlock.objects.filter(is_active=True).order_by("sort_order", "title")

    tasting_preview = TastingNote.objects.select_related("product").order_by("-created_at")[:3]
    guides_preview = BrewingGuide.objects.filter(is_published=True).order_by("-created_at")[:3]

    now = timezone.now()
    journal_preview = BlogPost.objects.filter(
        Q(status="published") | Q(status="scheduled", published_at__lte=now)
    ).order_by("-published_at", "-created_at")[:3]

    return render(request, "storefront/home.html", {
        "featured_products": featured,
        "featured_coffee": featured_coffee,
        "featured_tea": featured_tea,
        "gift_sets": gift_sets,
        "categories": categories,
        "campaigns": campaigns,
        "fundraising_feature": fundraising_feature,
        "promo_blocks": promo_blocks,
        "tasting_preview": tasting_preview,
        "guides_preview": guides_preview,
        "journal_preview": journal_preview,
    })


def product_list(request, category_type=None):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    current_category = None
    collection = request.GET.get("collection", "")
    if category_type:
        categories_filtered = Category.objects.filter(category_type=category_type, is_active=True)
        products = products.filter(category__in=categories_filtered)
        current_category = category_type
    cat_id = request.GET.get("category")
    if cat_id:
        products = products.filter(category_id=cat_id)
    sort = request.GET.get("sort", "-created_at")
    if sort in ["price", "-price", "name", "-name", "-created_at"]:
        products = products.order_by(sort)
    q = request.GET.get("q", "")
    if q:
        products = products.filter(name__icontains=q)

    if collection == "featured":
        products = products.filter(is_featured=True)
    elif collection == "new-arrivals":
        products = products.order_by("-created_at")
    elif collection == "value-finds":
        products = products.filter(compare_price__isnull=False)

    return render(request, "storefront/product_list.html", {
        "products": products,
        "categories": categories,
        "current_category": current_category,
        "search_query": q,
        "current_collection": collection,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    product_guides = product.brewing_guides.filter(is_published=True)[:3]
    approved_reviews = product.reviews.filter(status="approved").select_related("user")
    review_count = approved_reviews.count()
    avg_rating = 0
    if review_count:
        avg_rating = round(sum(r.rating for r in approved_reviews) / review_count, 1)

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

    return render(request, "storefront/product_detail.html", {
        "product": product,
        "related_products": related,
        "product_guides": product_guides,
        "is_coffee": product.category.category_type == "coffee",
        "is_tea": product.category.category_type == "tea",
        "reviews": approved_reviews,
        "review_count": review_count,
        "avg_rating": avg_rating,
        "in_wishlist": in_wishlist,
    })


def brewing_guides(request):
    guides = BrewingGuide.objects.filter(is_published=True)
    q = request.GET.get("q", "").strip()
    guide_type = request.GET.get("guide_type", "")
    level = request.GET.get("level", "")

    if q:
        guides = guides.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(method__icontains=q)
            | Q(tags__icontains=q)
        )
    if guide_type:
        guides = guides.filter(guide_type=guide_type)
    if level:
        guides = guides.filter(audience_level=level)

    beginner_guides = guides.filter(audience_level="beginner")[:6]
    premium_guides = guides.filter(is_premium_featured=True)[:4]
    if not premium_guides:
        premium_guides = guides.filter(audience_level="advanced")[:4]

    guide_type_sections = {
        "pour_over": guides.filter(guide_type="pour_over")[:4],
        "french_press": guides.filter(guide_type="french_press")[:4],
        "espresso_basics": guides.filter(guide_type="espresso_basics")[:4],
        "tea_steeping": guides.filter(guide_type="tea_steeping")[:4],
        "matcha_preparation": guides.filter(guide_type="matcha_preparation")[:4],
    }

    return render(request, "storefront/brewing_guides.html", {
        "guides": guides,
        "beginner_guides": beginner_guides,
        "premium_guides": premium_guides,
        "guide_type_sections": guide_type_sections,
        "search_query": q,
        "current_guide_type": guide_type,
        "current_level": level,
        "guide_type_choices": BrewingGuide.GUIDE_TYPE_CHOICES,
    })


def brewing_guide_detail(request, slug):
    guide = get_object_or_404(BrewingGuide, slug=slug, is_published=True)
    return render(request, "storefront/brewing_guide_detail.html", {"guide": guide})


def ritual(request):
    return render(request, "storefront/ritual.html")


def tasting_notes(request):
    notes = TastingNote.objects.select_related("product").all()
    q = request.GET.get("q", "").strip()
    tag = request.GET.get("tag", "").strip().lower()

    if q:
        notes = notes.filter(
            Q(title__icontains=q)
            | Q(body__icontains=q)
            | Q(aroma__icontains=q)
            | Q(flavor__icontains=q)
            | Q(finish__icontains=q)
            | Q(origin__icontains=q)
            | Q(pairings__icontains=q)
            | Q(style_notes__icontains=q)
            | Q(tags__icontains=q)
            | Q(product__name__icontains=q)
        )

    if tag:
        notes = notes.filter(tags__icontains=tag)

    notes = list(notes.order_by("-created_at")[:80])
    for note in notes:
        note.tag_list = _split_tags(note.tags)

    all_tags = set()
    for note in TastingNote.objects.exclude(tags="").values_list("tags", flat=True):
        all_tags.update(_split_tags(note))

    return render(request, "storefront/tasting_notes.html", {
        "notes": notes,
        "search_query": q,
        "current_tag": tag,
        "all_tags": sorted(all_tags),
    })


def fundraising_list(request):
    campaigns = FundraisingCampaign.objects.filter(status="active")
    return render(request, "storefront/fundraising.html", {"campaigns": campaigns})


def fundraising_detail(request, slug):
    campaign = get_object_or_404(FundraisingCampaign, slug=slug)
    return render(request, "storefront/fundraising_detail.html", {"campaign": campaign})


def campaign_landing(request, slug):
    landing = get_object_or_404(CampaignLandingPage, slug=slug, is_active=True)
    return render(request, "storefront/campaign_landing.html", {
        "landing": landing,
    })


def ritual_journal(request):
    now = timezone.now()
    posts = BlogPost.objects.filter(
        Q(status="published") | Q(status="scheduled", published_at__lte=now)
    ).order_by("-published_at", "-created_at")

    q = request.GET.get("q", "").strip()
    entry_type = request.GET.get("entry_type", "").strip()
    tag = request.GET.get("tag", "").strip().lower()

    if q:
        posts = posts.filter(
            Q(title__icontains=q)
            | Q(excerpt__icontains=q)
            | Q(body__icontains=q)
            | Q(tags__icontains=q)
        )
    if entry_type:
        posts = posts.filter(entry_type=entry_type)
    if tag:
        posts = posts.filter(tags__icontains=tag)

    all_tags = set()
    for tag_string in BlogPost.objects.exclude(tags="").values_list("tags", flat=True):
        all_tags.update(_split_tags(tag_string))

    featured_post = posts.first()
    remaining_posts = posts[1:15] if featured_post else posts[:15]

    return render(request, "storefront/ritual_journal.html", {
        "featured_post": featured_post,
        "posts": remaining_posts,
        "search_query": q,
        "current_entry_type": entry_type,
        "current_tag": tag,
        "entry_type_choices": BlogPost.ENTRY_TYPE_CHOICES,
        "all_tags": sorted(all_tags),
    })


def ritual_journal_detail(request, slug):
    now = timezone.now()
    post = get_object_or_404(
        BlogPost,
        slug=slug,
    )
    is_visible = post.status == "published" or (post.status == "scheduled" and post.published_at and post.published_at <= now)
    if not is_visible:
        return redirect("storefront:ritual_journal")

    related_posts = BlogPost.objects.filter(
        Q(status="published") | Q(status="scheduled", published_at__lte=now)
    ).exclude(pk=post.pk).order_by("-published_at")[:3]

    return render(request, "storefront/ritual_journal_detail.html", {
        "post": post,
        "related_posts": related_posts,
        "post_tags": _split_tags(post.tags),
    })


def about(request):
    page = Page.objects.filter(slug="about").first()
    return render(request, "storefront/about.html", {
        "page": page,
        "page_visual_alt": _page_image_alt(page, "About page visual"),
    })


def contact(request):
    if request.method == "POST":
        messages.success(request, "Thank you for your message. We'll be in touch.")
        return redirect("storefront:contact")
    return render(request, "storefront/contact.html")


def policies(request, slug="shipping"):
    page = Page.objects.filter(slug=slug).first()
    fallback = POLICY_FALLBACKS.get(slug, {})
    return render(request, "storefront/policies.html", {
        "page": page,
        "page_visual_alt": _page_image_alt(page, "Policy page visual"),
        "policy_slug": slug,
        "policy_title": fallback.get("title", "Policies"),
        "policy_body": fallback.get("body", "<p>Policy content coming soon. Please contact us with any questions.</p>"),
    })


def info_page(request, slug):
    page = Page.objects.filter(slug=slug).first()
    fallback = INFO_PAGE_FALLBACKS.get(slug, {})
    return render(request, TEMPLATE_INFO_PAGE, {
        "page": page,
        "page_visual_alt": _page_image_alt(page, "Page visual"),
        "title": page.title if page else fallback.get("title", "Information"),
        "body": page.body if page else fallback.get("body", INFO_BODY_FALLBACK),
    })


def faq(request):
    return info_page(request, "faq")


def wholesale(request):
    page, fallback = _get_page_with_fallback("wholesale", INFO_PAGE_FALLBACKS)
    if request.method == "POST":
        form = WholesaleInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            enqueue(
                send_inquiry_notification,
                "New wholesale inquiry",
                f"Wholesale inquiry received from {inquiry.name} ({inquiry.email}) for {inquiry.company_name}.",
            )
            messages.success(request, "Thank you. Our wholesale team will contact you shortly.")
            return redirect("storefront:wholesale")
    else:
        form = WholesaleInquiryForm()

    return render(request, TEMPLATE_INFO_PAGE, {
        "page": page,
        "title": page.title if page else fallback.get("title", "Wholesale"),
        "body": page.body if page else fallback.get("body", INFO_BODY_FALLBACK),
        "inquiry_form": form,
        "inquiry_heading": "Wholesale Inquiry",
        "inquiry_submit_label": "Send Wholesale Inquiry",
    })


def ambassador_program(request):
    page, fallback = _get_page_with_fallback("ambassador-program", INFO_PAGE_FALLBACKS)
    if request.method == "POST":
        form = AmbassadorInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            enqueue(
                send_inquiry_notification,
                "New ambassador inquiry",
                f"Ambassador inquiry received from {inquiry.name} ({inquiry.email}) on {inquiry.primary_platform}.",
            )
            messages.success(request, "Thanks for applying. We review ambassador requests weekly.")
            return redirect("storefront:ambassador_program")
    else:
        form = AmbassadorInquiryForm()

    return render(request, TEMPLATE_INFO_PAGE, {
        "page": page,
        "title": page.title if page else fallback.get("title", "Ambassador Program"),
        "body": page.body if page else fallback.get("body", INFO_BODY_FALLBACK),
        "inquiry_form": form,
        "inquiry_heading": "Ambassador Inquiry",
        "inquiry_submit_label": "Submit Ambassador Application",
    })


# Cart (session-based)
def _get_cart(request):
    return request.session.get("cart", {})


def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def cart_view(request):
    cart = _get_cart(request)
    items = []
    subtotal = Decimal("0.00")
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=pid, is_active=True)
            if product.stock_available is not None and qty > product.stock_available:
                qty = max(product.stock_available, 0)
                if qty == 0:
                    continue
                cart[pid] = qty
            line_total = product.price * qty
            items.append({"product": product, "quantity": qty, "line_total": line_total})
            subtotal += line_total
        except Product.DoesNotExist:
            continue

    _save_cart(request, cart)
    pricing = _build_pricing(subtotal)

    return render(request, "storefront/cart.html", {
        "items": items,
        "subtotal": subtotal,
        "pricing": pricing,
    })


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_cart(request)
    pid = str(product_id)
    qty = int(request.POST.get("quantity", 1))
    requested_qty = cart.get(pid, 0) + qty

    if product.stock_available is not None and requested_qty > product.stock_available:
        if product.stock_available <= 0:
            messages.error(request, "This item is currently out of stock.")
            return redirect(product.get_absolute_url())
        cart[pid] = product.stock_available
        messages.warning(request, f"Only {product.stock_available} units available. Cart updated.")
    else:
        cart[pid] = requested_qty

    _save_cart(request, cart)
    messages.success(request, "Added to cart.")
    if request.htmx:
        return cart_view(request)
    return redirect(URL_CART)


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_cart(request)
    pid = str(product_id)
    qty = int(request.POST.get("quantity", 0))
    if qty > 0:
        if product.stock_available is not None and qty > product.stock_available:
            cart[pid] = product.stock_available
            messages.warning(request, f"Only {product.stock_available} units available.")
        else:
            cart[pid] = qty
    else:
        cart.pop(pid, None)
    _save_cart(request, cart)
    return redirect(URL_CART)


@require_POST
def cart_remove(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect(URL_CART)


def checkout(request):
    cart = _get_cart(request)
    if not cart:
        return redirect(URL_CART)

    business_settings = BusinessSettings.load()
    shipping_method = request.POST.get("shipping_method") or request.GET.get("shipping_method") or request.session.get("shipping_method", "standard")
    items, subtotal, adjusted_cart, adjusted_products = _cart_items_with_stock(cart)

    for product_name in adjusted_products:
        messages.warning(request, f"{product_name} quantity adjusted based on current stock.")

    _save_cart(request, adjusted_cart)

    promo_code = request.POST.get("promo_code") or request.GET.get("promo_code") or request.session.get("promo_code", "")
    pricing = _build_pricing(subtotal, promo_code=promo_code, shipping_method=shipping_method)

    if request.method == "POST":
        return _checkout_submit(request, items, subtotal, pricing, shipping_method)

    return render(request, "storefront/checkout.html", {
        "items": items,
        "subtotal": subtotal,
        "pricing": pricing,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "business_settings": business_settings,
        "shipping_method": shipping_method,
    })


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "storefront/order_confirmation.html", {"order": order})


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get("email", "").strip()
    if not email:
        return _newsletter_success_response()

    defaults = _newsletter_tracking_defaults(request)
    subscriber, created = EmailSubscriber.objects.get_or_create(email=email, defaults=defaults)
    if not created:
        _update_subscriber_tracking(subscriber, defaults)
    messages.success(request, "Thank you for subscribing.")
    return _newsletter_success_response()


def _newsletter_success_response():
    return redirect(URL_HOME)


def _newsletter_tracking_defaults(request):
    source_raw = request.POST.get("source") or request.META.get("HTTP_REFERER", "direct")
    return {
        "source": source_raw[:100],
        "referral_code": (request.POST.get("ref") or request.session.get("tracking_ref", ""))[:80],
        "utm_source": (request.POST.get("utm_source") or request.session.get("tracking_utm_source", ""))[:120],
        "utm_medium": (request.POST.get("utm_medium") or request.session.get("tracking_utm_medium", ""))[:120],
        "utm_campaign": (request.POST.get("utm_campaign") or request.session.get("tracking_utm_campaign", ""))[:120],
        "landing_path": (request.POST.get("landing_path") or request.session.get("tracking_landing_path", request.path))[:255],
    }


def _get_page_with_fallback(slug, fallback_map):
    page = Page.objects.filter(slug=slug).first()
    return page, fallback_map.get(slug, {})


def _page_image_alt(page, fallback):
    if not page:
        return fallback
    return (page.image_alt or "").strip() or fallback


def _update_subscriber_tracking(subscriber, defaults):
    changed = False
    for field, value in defaults.items():
        if value and getattr(subscriber, field) != value:
            setattr(subscriber, field, value)
            changed = True
    if changed:
        subscriber.save()


def _split_tags(value):
    return [part.strip().lower() for part in value.split(",") if part.strip()]


def _build_pricing(subtotal, promo_code="", shipping_method="standard"):
    business_settings = BusinessSettings.load()

    shipping_options = {
        "standard": Decimal("0.00") if subtotal >= business_settings.free_shipping_threshold else Decimal("6.95"),
        "express": Decimal("14.95"),
        "overnight": Decimal("29.95"),
    }
    shipping_cost = shipping_options.get(shipping_method, shipping_options["standard"])

    coupon, discount, applied_promo_code = _resolve_coupon_discount(subtotal, promo_code)

    taxable_subtotal = subtotal - discount
    tax = taxable_subtotal * business_settings.tax_rate
    total = taxable_subtotal + shipping_cost + tax

    return {
        "coupon": coupon,
        "applied_promo_code": applied_promo_code,
        "discount": discount.quantize(Decimal("0.01")),
        "shipping_cost": shipping_cost.quantize(Decimal("0.01")),
        "tax": tax.quantize(Decimal("0.01")),
        "total": total.quantize(Decimal("0.01")),
    }


def _resolve_coupon_discount(subtotal, promo_code):
    entered_code = (promo_code or "").strip().upper()
    if not entered_code:
        return None, Decimal("0.00"), ""

    coupon = Coupon.objects.filter(code__iexact=entered_code, is_active=True).first()
    if not coupon:
        return None, Decimal("0.00"), ""

    now = timezone.now()
    within_dates = coupon.valid_from <= now <= coupon.valid_until
    within_usage = coupon.max_uses is None or coupon.times_used < coupon.max_uses
    meets_min_order = subtotal >= coupon.min_order
    if not (within_dates and within_usage and meets_min_order):
        return None, Decimal("0.00"), ""

    if coupon.discount_type == "percent":
        discount = (subtotal * coupon.discount_value) / Decimal("100")
    else:
        discount = coupon.discount_value

    if discount > subtotal:
        discount = subtotal
    return coupon, discount, coupon.code


def _cart_items_with_stock(cart):
    items = []
    subtotal = Decimal("0.00")
    adjusted_cart = dict(cart)
    adjusted_products = []

    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=pid, is_active=True)
        except Product.DoesNotExist:
            continue

        adjusted_qty = qty
        if product.stock_available is not None and qty > product.stock_available:
            adjusted_qty = max(product.stock_available, 0)
            adjusted_products.append(product.name)

        if adjusted_qty == 0:
            adjusted_cart.pop(pid, None)
            continue

        adjusted_cart[pid] = adjusted_qty
        line_total = product.price * adjusted_qty
        items.append({"product": product, "quantity": adjusted_qty, "line_total": line_total})
        subtotal += line_total

    return items, subtotal, adjusted_cart, adjusted_products


def _checkout_submit(request, items, subtotal, pricing, shipping_method):
    gift_note = request.POST.get("gift_note", "").strip()
    request.session["promo_code"] = pricing["applied_promo_code"]
    request.session["shipping_method"] = shipping_method

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        email=request.POST.get("email", ""),
        first_name=request.POST.get("first_name", ""),
        last_name=request.POST.get("last_name", ""),
        phone=request.POST.get("phone", ""),
        shipping_line1=request.POST.get("shipping_line1", ""),
        shipping_line2=request.POST.get("shipping_line2", ""),
        shipping_city=request.POST.get("shipping_city", ""),
        shipping_state=request.POST.get("shipping_state", ""),
        shipping_postal=request.POST.get("shipping_postal", ""),
        shipping_country=request.POST.get("shipping_country", "US"),
        shipping_method=shipping_method,
        subtotal=subtotal,
        discount_total=pricing["discount"],
        promo_code=pricing["applied_promo_code"],
        shipping_cost=pricing["shipping_cost"],
        tax=pricing["tax"],
        total=pricing["total"],
        gift_note=gift_note,
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            product_name=item["product"].name,
            product_sku=item["product"].sku,
            quantity=item["quantity"],
            unit_price=item["product"].price,
            total_price=item["line_total"],
        )

    if pricing["coupon"]:
        pricing["coupon"].times_used += 1
        pricing["coupon"].save(update_fields=["times_used"])

    return _finalize_checkout_payment(request, order, pricing)


def _finalize_checkout_payment(request, order, pricing):
    if settings.STRIPE_SECRET_KEY:
        intent = stripe.PaymentIntent.create(
            amount=int(pricing["total"] * 100),
            currency="usd",
            metadata={"order_number": order.order_number},
        )
        order.stripe_payment_intent = intent.id
        order.save(update_fields=["stripe_payment_intent"])
        request.session["cart"] = {}
        return render(request, "storefront/checkout_payment.html", {
            "order": order,
            "client_secret": intent.client_secret,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        })

    order.status = "confirmed"
    order.save(update_fields=["status"])
    request.session["cart"] = {}
    return redirect("storefront:order_confirmation", order_number=order.order_number)
