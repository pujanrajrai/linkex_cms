from django.urls import path
from . import views

app_name = "country"

urlpatterns = [
    path("list/", views.country_list, name="list"),
    path("create/", views.country_create, name="create"),
    path("update/<str:pk>/", views.country_update, name="update"),
    path("delete/", views.country_delete, name="delete"),
]
