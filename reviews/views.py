from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from orders.models import OrderItem
from .models import Review


@login_required
@require_POST
def review_create(request, product_id):
    """Submit a product review."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if Review.objects.filter(product=product, user=request.user).exists():
        messages.info(request, "You have already reviewed this product.")
        return redirect(product.get_absolute_url())

    is_verified = OrderItem.objects.filter(
        order__user=request.user, product=product
    ).exists()

    Review.objects.create(
        product=product,
        user=request.user,
        rating=int(request.POST.get("rating", 5)),
        title=request.POST.get("title", ""),
        body=request.POST.get("body", ""),
        is_verified_purchase=is_verified,
    )
    messages.success(request, "Thank you for your review. It will appear after moderation.")
    return redirect(product.get_absolute_url())
