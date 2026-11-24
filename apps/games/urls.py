from django.urls import path
from . import views

app_name = "games"

urlpatterns = [
    path("", views.game_list, name="list"),
    path("add/", views.add_game, name="add"),
    path("remove/", views.remove_game, name="remove"),
    path("clear/", views.clear_cart, name="clear"),
]