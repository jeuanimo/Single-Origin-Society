from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from products.models import Product
from orders.models import Order, OrderItem
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

URL_CART = "storefront:cart"


def _get_cart(request):
    return request.session.get("cart", {})


def checkout_view(request):
    """Display checkout form and process order submission."""
    cart = _get_cart(request)
    if not cart:
        return redirect(URL_CART)

    items = []
    total = 0
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=pid, is_active=True)
            line_total = product.price * qty
            items.append({"product": product, "quantity": qty, "line_total": line_total})
            total += line_total
        except Product.DoesNotExist:
            continue

    if request.method == "POST":
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
            subtotal=total,
            total=total,
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
        if settings.STRIPE_SECRET_KEY:
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
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

    return render(request, "storefront/checkout.html", {
        "items": items,
        "total": total,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    })


def order_confirmation(request, order_number):
    """Display order confirmation after successful checkout."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "storefront/order_confirmation.html", {"order": order})


@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events for payment confirmation.

    CSRF exemption is applied via the URL configuration using
    django.views.decorators.csrf.csrf_exempt on the path, because
    Stripe cannot send a Django CSRF token. Authentication is provided
    by Stripe’s webhook signature verification below.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order_number = intent.get("metadata", {}).get("order_number")
        if order_number:
            Order.objects.filter(order_number=order_number).update(status="confirmed")

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        order_number = intent.get("metadata", {}).get("order_number")
        if order_number:
            Order.objects.filter(order_number=order_number).update(status="cancelled")

    return HttpResponse(status=200)
