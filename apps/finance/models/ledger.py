from django.db.models import Sum
from accounts.models import Agency, Company
from django.db import models
from base.models import BaseModel
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

ledger_type = [
    ('DEBIT', 'DEBIT'),
    ('CREDIT', 'CREDIT')
]
entry_type = [
    ('LEDGER ENTRY', 'LEDGER ENTRY'),
    ('INVOICE', 'INVOICE'),
    ('PAYMENT', 'PAYMENT'),
    ('ADJUSTMENT', 'ADJUSTMENT'),
    ('OTHER', 'OTHER')
]
reference_type = [
    ('AWB', 'AWB'),
    ('INVOICE', 'INVOICE'),
    ('PAYMENT', 'PAYMENT'),
]


class Ledger(BaseModel):
    agency = models.ForeignKey(
        Agency, on_delete=models.CASCADE, editable=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, editable=False)
    ledger_type = models.CharField(
        max_length=10, choices=ledger_type, editable=False)
    entry_type = models.CharField(
        max_length=20, choices=entry_type, editable=False)
    particular = models.CharField(max_length=255, editable=False)
    amount = models.FloatField(editable=False)
    company_balance = models.FloatField(editable=False)
    balance = models.FloatField(editable=False)
    reference_no = models.CharField(
        max_length=255, blank=True, null=True, editable=False)
    reference = models.CharField(
        max_length=255, blank=True, null=True, editable=False, choices=reference_type)
    remarks = models.TextField(blank=True, null=True, editable=False)
    is_cancelled = models.BooleanField(default=False, editable=False)
    json_remarks = models.JSONField(blank=True, null=True, editable=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.agency.company_name} - {self.company.name} - {self.particular} - {self.amount}"

    @classmethod
    def get_last_balance(cls, agency):
        """Returns the latest agency ledger balance. If no ledger is found, returns 0."""
        try:
            last_ledger = cls.objects.filter(
                agency=agency).latest('created_at')
            return last_ledger.balance
        except Exception as e:
            return 0

    @classmethod
    def get_last_company_balance(cls, agency, company):
        """Returns the latest company ledger balance for the given agency and company. If no ledger is found, returns 0."""
        try:
            last_ledger = cls.objects.filter(
                agency=agency, company=company).latest('created_at')
            return last_ledger.company_balance
        except cls.DoesNotExist:
            return 0


def get_last_balance(agency, company):
    return Ledger.get_last_company_balance(agency, company)


@receiver(pre_save, sender=Ledger)
def calculate_ledger_balances(sender, instance, **kwargs):
    """Calculate balances before saving the ledger entry"""
    if not instance.pk:  # Only for new entries
        # Get last balances
        last_agency_balance = Ledger.get_last_balance(instance.agency)
        last_company_balance = Ledger.get_last_company_balance(
            instance.agency, instance.company)
        # Calculate new balances based on ledger type
        amount = float(instance.amount)
        if instance.ledger_type == 'DEBIT':
            instance.balance = last_agency_balance - amount
            instance.company_balance = last_company_balance - amount
        else:  # Credit
            instance.balance = last_agency_balance + amount
            instance.company_balance = last_company_balance + amount
