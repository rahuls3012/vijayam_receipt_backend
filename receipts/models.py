from django.conf import settings
from django.db import models, transaction
from django.db.models import Max
from .utils import amount_to_words


class Receipt(models.Model):
    class Mode(models.TextChoices):
        CASH = "cash", "Cash"
        GPAY = "gpay", "GPay / UPI"
        CHEQUE = "cheque", "Cheque"
        BANK = "bank", "Bank transfer"

    receipt_no = models.PositiveIntegerField(unique=True, editable=False)
    date = models.DateField()
    received_from = models.CharField("Received with thanks from M/s.", max_length=150, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_in_words = models.CharField(max_length=255, editable=False)
    towards = models.CharField(max_length=200, help_text="e.g. MBA Finance")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.CASH)
    cashier = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-receipt_no"]

    def save(self, *args, **kwargs):
        self.amount_in_words = amount_to_words(self.amount)
        with transaction.atomic():
            if not self.receipt_no:
                last = Receipt.objects.aggregate(m=Max("receipt_no"))["m"]
                self.receipt_no = (last + 1) if last else settings.RECEIPT_START_NO
            super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.receipt_no} {self.received_from}"
