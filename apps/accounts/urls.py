from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.start, name="start"),
    path("logout/", views.logout_view, name="logout"),
]