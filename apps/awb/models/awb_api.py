from django.db import models
from awb.models.awb import AWBDetail
from base.models import BaseModel
from hub.models import Vendor


class AWBAPI(BaseModel):
    awb = models.ForeignKey(AWBDetail, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    api_response = models.TextField()
    api_response_json = models.JSONField()
    is_success = models.BooleanField(default=False)
    response_code = models.CharField(max_length=255)
    response_message = models.TextField()

    def __str__(self):
        return self.awb.awbno
