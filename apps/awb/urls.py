from django.urls import path, include
app_name = "awb"
urlpatterns = [

    path(
        'pages/', include('awb.pages.urls'),
    ),
    path(
        'apis/', include('awb.apis.urls')
    )
]
