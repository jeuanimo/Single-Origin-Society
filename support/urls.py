from django.urls import path
from . import views

app_name = "support"

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("new/", views.ticket_create, name="ticket_create"),
    path("<str:ticket_number>/", views.ticket_detail, name="ticket_detail"),
]
