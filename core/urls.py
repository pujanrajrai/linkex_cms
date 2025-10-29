from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from hub.pages.run.views import run_history
from django.views.generic import TemplateView
from django.urls import path, include
from decouple import config
from . import views
settings_key = config('SETTINGS_KEY', default='local')

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('awb/', include('awb.urls')),
    path('hub/', include('hub.urls')),
    path('company/', include('home.urls')),
    path('finance/', include('finance.urls')),
    path('captcha/', include('captcha.urls')),
    path('captcha/', include('captcha.urls')),
    path('', views.home, name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('agency_request/', views.agency_request, name='agency_request'),

    path('tracking/', views.tracking, name='tracking'),
    path('history/deleted/records/',
         views.get_deleted_models, name='get_deleted_models'),
    path('history/', views.history_list, name='history_list'),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include the debug toolbar URLs only in local or dev settings
if settings_key == "local" or settings_key == "dev":
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns

    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk'))
    ]
