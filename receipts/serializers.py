from rest_framework import serializers
from .models import Receipt


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ["id", "receipt_no", "date", "received_from", "amount", "amount_in_words",
                  "towards", "balance", "payment_mode", "cashier", "created_at"]
        read_only_fields = ["receipt_no", "amount_in_words", "created_at"]

    def validate_amount(self, v):
        if v <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return v
