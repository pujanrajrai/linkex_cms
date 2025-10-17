from django.urls import path
from . import views

app_name = "agency"

urlpatterns = [
    path("list/", views.agency_list, name="list"),
    path("request_list/", views.agency_request_list, name="request_list"),
    path("create/", views.agency_create, name="create"),
    path("update/<int:pk>/", views.agency_update, name="update"),
    path("detail/<int:pk>/", views.agency_detail, name="detail"),
    path("block/<int:pk>/", views.agency_block, name="block"),
    path("unblock/<int:pk>/", views.agency_unblock, name="unblock"),
    path("add-user/<int:pk>", views.add_user_in_agency, name="add_agency_user"),
    path('add-hub-rate/<int:pk>', views.add_agency_hub_rate,
         name='add_agency_hub_rate'),
    path('upload/agency-hub-rate/<int:pk>',
         views.upload_agency_hub_rate, name="upload_agency_hub_rate"),
    path('edit/agency/<int:agency_pk>/hub-rate/<int:bzs_pk>',
         views.edit_agency_hub_rate, name="edit_agency_hub_rate"),
    path('history/<int:agency_id>/', views.user_history_by_agency,
         name='user_history_by_agency'),
    path('hub_rate/history/<int:agency_id>/',
         views.agency_hub_rate_history, name='agency_hub_rate_history'),
    path('submit-agency-request/', views.submit_agency_request,
         name='submit_agency_request'),


]
