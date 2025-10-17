from django.db import models
from base.models import BaseModel
from hub.models import Vendor


class VendorLoginCred(BaseModel):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    additional_cred1 = models.CharField(max_length=255, blank=True, null=True)
    additional_cred2 = models.CharField(max_length=255, blank=True, null=True)
    additional_cred3 = models.CharField(max_length=255, blank=True, null=True)
    additional_cred4 = models.CharField(max_length=255, blank=True, null=True)
