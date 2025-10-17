from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# from awb.models import AWBDetail
# Register your models here.

from awb.models import AWBDetail, AWBStatus, ProductType, Service, Consignee, Consignor, BoxDetails, BoxItem, DocumentType, HSCODE, UnitType, AWBAPIResponse
admin.site.register([AWBDetail,
                     DocumentType, HSCODE, UnitType, ProductType, Service,
                    Consignee, Consignor, BoxDetails, BoxItem, AWBStatus], SimpleHistoryAdmin)


@admin.register(AWBAPIResponse)
class AWBAPIResponseAdmin(SimpleHistoryAdmin):
    list_display = ('awb', 'vendor', 'is_success', 'awbno_from_response')
    list_filter = ('vendor', 'is_success')
    search_fields = ('awb__awbno', 'vendor')
    raw_id_fields = ('awb',)
    readonly_fields = ('awb', 'vendor', 'is_success')
    list_per_page = 20

    def awbno_from_response(self, obj):
        try:
            return obj.response.get("AWBNo", "")
        except Exception:
            return ""
    awbno_from_response.short_description = "AWBNo"
