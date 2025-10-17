from accounts.models.masters import Country
from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords


class Company(BaseModel):
    history = HistoricalRecords()

    name = models.CharField(max_length=30, unique=True)
    address1 = models.CharField(max_length=255, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    post_zip_code = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)
    state_county = models.CharField(max_length=100, null=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return self.name
