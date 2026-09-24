from django.urls import path
from tickets import views

urlpatterns = [
    path("", views.ticket_list, name="ticket-list"),
    path("create/", views.ticket_create, name="ticket-create"),
    path("<int:ticket_id>/", views.ticket_detail, name="ticket-detail"),
]
