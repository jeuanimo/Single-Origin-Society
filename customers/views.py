from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.urls import resolve, reverse, Resolver404
from django.utils.http import url_has_allowed_host_and_scheme
from products.models import Product
from .models import WishlistItem


def _safe_next_redirect(request, next_url):
    if not next_url:
        return None
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return None
    try:
        match = resolve(next_url)
        return reverse(match.url_name, args=match.args, kwargs=match.kwargs)
    except (Resolver404, Exception):
        return None


@login_required
def wishlist_view(request):
    """Display wishlist items for the signed-in customer."""
    items = WishlistItem.objects.filter(user=request.user).select_related("product", "product__category")
    return render(request, "customers/wishlist.html", {"items": items})


@login_required
@require_POST
def wishlist_add(request, product_id):
    """Add a product to the user's wishlist."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.name} added to wishlist.")
    next_url = _safe_next_redirect(request, request.POST.get("next"))
    if next_url:
        return redirect(next_url)
    return redirect("storefront:product_detail", slug=product.slug)


@login_required
@require_POST
def wishlist_remove(request, product_id):
    """Remove a product from the wishlist."""
    WishlistItem.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, "Removed from wishlist.")
    next_url = _safe_next_redirect(request, request.POST.get("next"))
    if next_url:
        return redirect(next_url)
    return redirect("customers:wishlist")
