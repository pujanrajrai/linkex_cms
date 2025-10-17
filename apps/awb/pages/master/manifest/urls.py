from django.urls import path
from . import views

app_name = "manifest"

urlpatterns = [
    path("list/", views.manifest_list, name="list"),
    path("create/", views.manifest_create, name="create"),
    path("update/<str:pk>/", views.manifest_update, name="update"),
    path("delete/", views.manifest_delete, name="delete"),
]
