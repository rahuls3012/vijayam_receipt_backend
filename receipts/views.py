from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Receipt
from .pdf import build_receipt_pdf
from .serializers import ReceiptSerializer


class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer

    def get_queryset(self):
        qs = Receipt.objects.all()
        p = self.request.query_params
        if s := p.get("search"):
            q = Q(received_from__icontains=s) | Q(towards__icontains=s)
            if s.isdigit():
                q |= Q(receipt_no=int(s))
            qs = qs.filter(q)
        if d := p.get("date"):
            qs = qs.filter(date=d)
        if d := p.get("date_from"):
            qs = qs.filter(date__gte=d)
        if d := p.get("date_to"):
            qs = qs.filter(date__lte=d)
        if m := p.get("payment_mode"):
            qs = qs.filter(payment_mode=m)
        return qs

    def perform_create(self, serializer):
        cashier = serializer.validated_data.get("cashier") or self.request.user.get_full_name() or self.request.user.username
        serializer.save(cashier=cashier)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        r = self.get_object()
        resp = HttpResponse(build_receipt_pdf(r), content_type="application/pdf")
        kind = "attachment" if request.query_params.get("download") else "inline"
        resp["Content-Disposition"] = f'{kind}; filename="receipt-{r.receipt_no}.pdf"'
        return resp
