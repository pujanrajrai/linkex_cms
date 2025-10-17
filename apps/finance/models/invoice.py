from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from awb.models.awb import AWBDetail
from base.models import BaseModel
from .ledger import Ledger

payment_method_choices = [
    ('CASH', 'Cash'),
    ('BANK_TRANSFER', 'Bank Transfer'),
    ('CREDIT_CARD', 'Credit Card'),
    ('OTHER', 'Other')
]


def get_last_balance(agency, company):
    """Get the last balance for an agency and company"""
    try:
        last_ledger = Ledger.objects.filter(
            agency=agency,
            company=company
        ).order_by('-created_at').first()

        if last_ledger:
            return last_ledger.balance
        return 0.00
    except Exception:
        return 0.00


class Invoice(BaseModel):
    awb = models.ForeignKey(
        AWBDetail,
        on_delete=models.PROTECT,
        related_name='invoices',
        help_text='The AWB that this invoice is for'
    )
    total_weight = models.FloatField()
    total_amount = models.FloatField()
    total_box = models.IntegerField()
    per_box_handling_fee = models.FloatField()
    per_kg_customs_fee = models.FloatField()

    grand_total = models.FloatField()
    total_paid_amount = models.FloatField()

    payment_method = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=payment_method_choices,
        help_text='The method of payment for this invoice'
    )

    remark = models.TextField(blank=True, null=True)
    document = models.FileField(upload_to='invoices/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.id} - AWB {self.awb.awbno}"

    def save(self, *args, **kwargs):
        # check in case of creation
        if self.pk is None:
            if Invoice.objects.filter(awb=self.awb, is_active=True).exists():
                raise ValidationError(
                    "There is already an active invoice for this AWB")
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     if self.is_active:
    #         Invoice.objects.filter(awb=self.awb).exclude(pk=self.pk).update(is_active=False)
    #     super().save(*args, **kwargs)


@receiver(post_save, sender=Invoice)
def handle_invoice_ledger_entries(sender, instance, created, **kwargs):
    """Handle ledger entries for invoice creation and cancellation"""

    # Skip if no agency (cash customer)
    if not instance.awb.agency:
        if created:
            instance.awb.is_invoice_generated = True
            instance.awb.save()
        elif not instance.is_active:
            instance.awb.is_invoice_generated = False
            instance.awb.save()
        return

    awb = instance.awb  # Use the existing AWB instance
    agency = awb.agency
    company = awb.company

    def create_ledger_entry(ledger_type, entry_type, particular, amount, remarks):
        """Helper function to create ledger entries"""
        return Ledger.objects.create(
            agency=agency,
            company=company,
            ledger_type=ledger_type,
            entry_type=entry_type,
            particular=particular,
            amount=amount,
            remarks=remarks,
            reference_no=instance.id,
            reference="INVOICE"
        )

    try:
        with transaction.atomic():
            if created:
                # Invoice creation - debit entry
                create_ledger_entry(
                    "DEBIT", "INVOICE",
                    f"Invoice #{instance.id} - AWB {awb.awbno}",
                    instance.grand_total,
                    f"Invoice Total Amount - AWB {awb.awbno}"
                )

                # Payment entry if paid amount exists
                if instance.total_paid_amount > 0:
                    create_ledger_entry(
                        "CREDIT", "PAYMENT",
                        f"Payment for Invoice #{instance.id}",
                        instance.total_paid_amount,
                        f"Invoice Payment - AWB {awb.awbno}"
                    )

                # Update AWB invoice status
                awb.is_invoice_generated = True
                awb.save(update_fields=['is_invoice_generated'])

            else:
                # Invoice update - check for cancellation
                if not instance.is_active:
                    # Reverse invoice amount
                    create_ledger_entry(
                        "CREDIT", "CANCEL_INVOICE",
                        f"Cancel Invoice #{instance.id} - AWB {awb.awbno}",
                        instance.grand_total,
                        f"Invoice Cancelled - AWB {awb.awbno}"
                    )

                    # Reverse payment if exists
                    if instance.total_paid_amount > 0:
                        create_ledger_entry(
                            "DEBIT", "CANCEL_PAYMENT",
                            f"Reverse Payment for Invoice #{instance.id}",
                            instance.total_paid_amount,
                            f"Payment Reversed - Invoice Cancelled - AWB {awb.awbno}"
                        )

                    # Update AWB invoice status
                    awb.is_invoice_generated = False
                    awb.save(update_fields=['is_invoice_generated'])

    except Exception as e:
        print(f"Error creating ledger entries for Invoice #{instance.id}: {e}")
        raise
