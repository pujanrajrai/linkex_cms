from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("list/", views.user_list, name="list"),
    path("create/", views.user_create, name="create"),
    path("update/<int:pk>/", views.user_update, name="update"),
    path("agency/<int:agency_pk>/update/<int:pk>", views.user_update, name="agency_user_update"),
    path("block/<int:pk>/", views.user_block, name="block"),
    path("change-password/<int:pk>", views.change_password, name="change_password"),
    path("agency/<int:agency_pk>/change-password/<int:pk>", views.change_password, name="agency_change_password"),
    path("unblock/<int:pk>/", views.user_unblock, name="unblock"),
]
