from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from hub.models import *

admin.site.register([Hub,
                     Run, RunAWB, RunStatus], SimpleHistoryAdmin)

admin.site.register(VendorLoginCred)
