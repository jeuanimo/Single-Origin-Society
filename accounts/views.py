from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import resolve, reverse, Resolver404
from django.utils.http import url_has_allowed_host_and_scheme
from customers.models import WishlistItem
from .forms import CustomerRegistrationForm, LoginForm, ProfileForm, AddressForm
from .models import Address

URL_HOME = "storefront:home"
URL_PROFILE = "accounts:profile"


def register_view(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to Single Origin Society!")
            return redirect(URL_HOME)
    else:
        form = CustomerRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_param = request.GET.get("next", "")
            if next_param and url_has_allowed_host_and_scheme(
                url=next_param,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                try:
                    match = resolve(next_param)
                    safe_url = reverse(
                        match.url_name, args=match.args, kwargs=match.kwargs
                    )
                    return redirect(safe_url)
                except (Resolver404, Exception):
                    pass
            if user.is_portal_user:
                return redirect("portal:dashboard")
            return redirect(URL_HOME)
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect(URL_HOME)


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect(URL_PROFILE)
    else:
        form = ProfileForm(instance=request.user)
    addresses = request.user.addresses.all()
    recent_orders = request.user.orders.prefetch_related("items")[:10]
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    return render(request, "accounts/profile.html", {
        "form": form,
        "addresses": addresses,
        "recent_orders": recent_orders,
        "wishlist_count": wishlist_count,
    })


@login_required
def address_add(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, "Address added.")
            return redirect(URL_PROFILE)
    else:
        form = AddressForm()
    return render(request, "accounts/address_form.html", {"form": form})


@login_required
def address_delete(request, pk):
    Address.objects.filter(pk=pk, user=request.user).delete()
    messages.success(request, "Address removed.")
    return redirect(URL_PROFILE)
