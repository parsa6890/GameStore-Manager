from django.urls import path
from . import views

app_name = "consoles"

urlpatterns = [
    path("select/", views.select, name="select"),
    path("save-capacity/", views.save_capacity, name="save_capacity"),
]