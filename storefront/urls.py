from django.urls import path
from . import views

app_name = "storefront"

urlpatterns = [
    path("", views.home, name="home"),
    # Product browsing
    path("shop/", views.product_list, name="shop"),
    path("shop/coffee/", views.product_list, {"category_type": "coffee"}, name="coffee"),
    path("shop/tea/", views.product_list, {"category_type": "tea"}, name="tea"),
    path("shop/accessories/", views.product_list, {"category_type": "accessories"}, name="accessories"),
    path("shop/drinkware/", views.product_list, {"category_type": "drinkware"}, name="drinkware"),
    path("shop/gift-sets/", views.product_list, {"category_type": "gift_sets"}, name="gift_sets"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    # Content
    path("brewing-guides/", views.brewing_guides, name="brewing_guides"),
    path("brewing-guides/<slug:slug>/", views.brewing_guide_detail, name="brewing_guide_detail"),
    path("ritual/", views.ritual, name="ritual"),
    path("tasting-notes/", views.tasting_notes, name="tasting_notes"),
    path("fundraising/", views.fundraising_list, name="fundraising"),
    path("fundraising/<slug:slug>/", views.fundraising_detail, name="fundraising_detail"),
    path("campaigns/<slug:slug>/", views.campaign_landing, name="campaign_landing"),
    path("ritual-journal/", views.ritual_journal, name="ritual_journal"),
    path("ritual-journal/<slug:slug>/", views.ritual_journal_detail, name="ritual_journal_detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("policies/", views.policies, name="policies"),
    path("policies/shipping/", views.policies, {"slug": "shipping"}, name="policy_shipping"),
    path("policies/refunds/", views.policies, {"slug": "refunds"}, name="policy_refunds"),
    path("policies/privacy/", views.policies, {"slug": "privacy"}, name="policy_privacy"),
    path("policies/terms/", views.policies, {"slug": "terms"}, name="policy_terms"),
    path("faq/", views.faq, name="faq"),
    path("wholesale/", views.wholesale, name="wholesale"),
    path("ambassador-program/", views.ambassador_program, name="ambassador_program"),
    path("policies/<slug:slug>/", views.policies, name="policy_page"),
    # Cart & Checkout
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<str:order_number>/", views.order_confirmation, name="order_confirmation"),
    # Newsletter
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
]
