from django.urls import path
from . import views

app_name = "currency"
urlpatterns = [
    path("list/", views.currency_list, name="list"),
    path("create/", views.currency_create, name="create"),
    path("update/<str:pk>/", views.currency_update, name="update"),
    path("delete/", views.currency_delete, name="delete"),
]
