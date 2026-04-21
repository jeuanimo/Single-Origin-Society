from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product

URL_CART = "storefront:cart"


def _get_cart(request):
    return request.session.get("cart", {})


def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def cart_detail(request):
    """Display shopping cart contents."""
    cart = _get_cart(request)
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
    return render(request, "storefront/cart.html", {"items": items, "total": total})


@require_POST
def cart_add(request, product_id):
    """Add a product to the session cart."""
    cart = _get_cart(request)
    pid = str(product_id)
    qty = int(request.POST.get("quantity", 1))
    cart[pid] = cart.get(pid, 0) + qty
    _save_cart(request, cart)
    messages.success(request, "Added to cart.")
    if request.htmx:
        return cart_detail(request)
    return redirect(URL_CART)


@require_POST
def cart_update(request, product_id):
    """Update quantity of a cart item."""
    cart = _get_cart(request)
    pid = str(product_id)
    qty = int(request.POST.get("quantity", 0))
    if qty > 0:
        cart[pid] = qty
    else:
        cart.pop(pid, None)
    _save_cart(request, cart)
    return redirect(URL_CART)


@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart."""
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect(URL_CART)
