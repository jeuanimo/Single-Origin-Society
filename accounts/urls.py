from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("address/add/", views.address_add, name="address_add"),
    path("address/<int:pk>/delete/", views.address_delete, name="address_delete"),
]
