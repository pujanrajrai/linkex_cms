from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from accounts.models import *
# Register your models here.
admin.site.register([User, Country, Agency, DividingFactor, AgencyAccess, Company, Currency, Module, ZipCode], SimpleHistoryAdmin)
admin.site.register(AgencyRequest)
