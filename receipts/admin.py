from django.contrib import admin
from .models import Receipt

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_no", "date", "received_from", "towards", "amount")
    search_fields = ("received_from", "receipt_no")
    list_filter = ("date", "payment_mode")
