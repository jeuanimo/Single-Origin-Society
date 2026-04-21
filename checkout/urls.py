from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = "checkout"

urlpatterns = [
    path("", views.checkout_view, name="checkout"),
    path("order/<str:order_number>/", views.order_confirmation, name="order_confirmation"),
    path("webhook/stripe/", csrf_exempt(views.stripe_webhook), name="stripe_webhook"),
]
