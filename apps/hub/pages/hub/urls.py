from django.urls import path
from . import views
app_name = 'hub'
urlpatterns = [
    path('create/', views.create_hub, name="create"),
    path('list/', views.list_hub, name="list"),
    path('detail/<str:pk>/', views.hub_detail, name="detail"),
    path('update/<str:pk>/', views.update_hub, name="update"),
    path('delete/<int:pk>/', views.delete_hub, name='delete'),
]
