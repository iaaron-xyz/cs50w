from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("add_new", views.add_new, name="add_new"),
    path("listing_page/<int:listing_id>", views.listing_page, name="listing_page"),
    path("place_bid/<int:owner_id>/<int:listing_id>", views.place_bid, name='place_bid'),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_watchlist/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
