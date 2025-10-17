from django.urls import path
from . import views
app_name = 'run'
urlpatterns = [

    path(
        'create/', views.create_run, name="create"
    ),
    path(
        'update/<int:run_id>/', views.update_run, name="update"
    ),
    path(
        'list/', views.list_run, name="list"
    ),
    path(
        'add-awb/<int:run_id>/', views.new_awb, name="add_awb"
    ),
    path('run/<int:run_id>/awbs/data/',
         views.run_awbs_data, name='run_awbs_data'),
    path('manifest-formats/', views.manifest_formats_data,
         name='manifest_formats_data'),
    path(
        'update-run-status/<int:run_id>/', views.update_run_status, name="update_run_status"
    ),
    path(
        'delete-run-status/<int:run_status_id>/', views.delete_run_status, name="delete_run_status"
    ),
    path(
        'import-all/<int:run_id>/', views.get_all_awb_from_company_and_hub, name="import_all"
    ),
    path(
        'add-new-awb/<int:run_id>/', views.add_new_awb_to_run, name="add_new_awb"
    ),
    path(
        'remove-awb/<str:run_id>/<str:awb_no>/', views.remove_awb_from_run, name="remove_awb"
    ),
    path("export-excel/<int:run_id>/",
         views.export_to_excel, name="export_excel"),
    path('history/<int:run_id>/', views.run_history, name='run_history'),
    path('lock/<int:run_id>/', views.lock_run, name='lock_run'),
    path('unlock/<int:run_id>/', views.unlock_run, name='unlock_run'),
    path('api/get-awb-details/', views.get_awb_details, name='get_awb_details'),
    path('api/get-vendor-default-manifest/',
         views.get_vendor_default_manifest, name='get_vendor_default_manifest'),
    path('get-hub-vendors/', views.get_hub_vendors, name='get_hub_vendors'),
]
