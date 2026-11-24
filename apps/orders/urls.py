from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("success/<str:order_number>/", views.order_success, name="success"),
    path("detail/<str:order_number>/<str:token>/", views.order_detail, name="detail"),
    path("my/", views.my_orders, name="my_orders"),
]