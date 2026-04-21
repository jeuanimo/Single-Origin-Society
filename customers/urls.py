from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views.wishlist_add, name="wishlist_add"),
    path("wishlist/remove/<int:product_id>/", views.wishlist_remove, name="wishlist_remove"),
]
