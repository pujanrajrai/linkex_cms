from django.db import models
from finance.models.invoice import Invoice
from base.models import BaseModel
from accounts.models import Agency, Company
from django.db.models.signals import post_save
from django.dispatch import receiver
from finance.models.ledger import Ledger


class PaymentMethodChoices(models.TextChoices):
    CASH = 'CASH', 'Cash'
    CHEQUE = 'CHEQUE', 'Cheque'


class Payment(BaseModel):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT, related_name='payments')
    amount = models.FloatField()
    remarks = models.TextField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethodChoices.choices,
        default=PaymentMethodChoices.CASH
    )
    file_upload = models.FileField(
        upload_to='payments/', null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    json_remarks = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.invoice.awb.awbno} - {self.amount}"


@receiver(post_save, sender=Payment)
def adding_ledger_record(sender, instance, created, **kwargs):
    Ledger.objects.create(
        agency=instance.invoice.awb.agency,
        company=instance.invoice.awb.company,
        ledger_type='CREDIT',
        entry_type='PAYMENT',
        amount=instance.amount,
        reference_no=instance.invoice.awb.awbno,
        reference=instance.invoice.awb.awbno,
    )
