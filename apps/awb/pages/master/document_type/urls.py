from django.urls import path
from . import views

app_name = 'document_type'

urlpatterns = [
    path('', views.document_type_list, name='list'),
    path('create/', views.document_type_create, name='create'),
    path('update/<str:pk>/', views.document_type_update, name='update'),
    path('delete/', views.document_type_delete, name='delete'),
]
