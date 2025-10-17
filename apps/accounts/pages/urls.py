from django.urls import path, include
app_name = "pages"
urlpatterns = [
    path('auth/', include('accounts.pages.auth.urls')),
    path('users/', include('accounts.pages.users.urls')),
    path('agency/', include('accounts.pages.agency.urls')),

]
