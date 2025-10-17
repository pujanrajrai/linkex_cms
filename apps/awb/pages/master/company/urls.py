from django.urls import path, include
from . import views
app_name = "company"


urlpatterns = [
    path(
        'list/', views.company_list, name="list"
    ),
    path(
        'create/', views.company_create, name="create"
    ),
    path(
        'update/<str:pk>/', views.company_update, name="update"
    ),
    path(
        'delete/', views.company_delete, name="delete"
    ),

]
