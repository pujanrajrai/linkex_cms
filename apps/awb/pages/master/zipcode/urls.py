from django.urls import path
from . import views

app_name = "zipcode"

urlpatterns = [
    path('search-city/', views.search_city, name='search'),
    path("list/", views.ZipCodeListView.as_view(), name="list"),
    path("create/", views.ZipCodeCreateView.as_view(), name="create"),
    path("update/<str:pk>/", views.ZipCodeUpdateView.as_view(), name="update"),
    path("delete/", views.zipcode_delete, name="delete"),
]
