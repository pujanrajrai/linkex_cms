from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords
from accounts.models import Agency

class PickupRequest(BaseModel):
    class PickupRequestStatus(models.TextChoices):
        PENDING = 'PENDING'
        ACCEPTED = 'ACCEPTED'
        REJECTED = 'REJECTED'
        COMPLETED = 'COMPLETED'
        CANCELLED = 'CANCELLED'

    history = HistoricalRecords()
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT)
    pickup_date = models.DateField()
    remarks = models.TextField(help_text="Any additional information about the pickup request")
    status = models.CharField(max_length=20, choices=PickupRequestStatus.choices, default=PickupRequestStatus.PENDING)
    admin_remarks = models.TextField(help_text="Any additional information about the pickup request by admin", null=True, blank=True)

    def __str__(self):
        return f"Pickup Request for {self.agency.name} on {self.pickup_date}"

