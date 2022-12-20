from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="article"),
    path("search", views.search, name="search"),
    path("create", views.create, name="create")
]
